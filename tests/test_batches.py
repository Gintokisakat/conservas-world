"""Tests del seguimiento de fermentos por usuario (3.1)."""

import uuid

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture()
def client(session_factory):
    from app.db.database import get_session

    from tests.conftest import _seed

    TestingSessionLocal = session_factory

    session = TestingSessionLocal()
    _seed(session)
    session.commit()
    session.close()

    def _override():
        s = TestingSessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_session] = _override
    from app.services import auth as auth_svc

    auth_svc._attempts.clear()
    yield TestClient(app)
    app.dependency_overrides.pop(get_session, None)
    auth_svc._attempts.clear()


def _register(client):
    email = f"batch_{uuid.uuid4().hex[:10]}@example.com"
    r = client.post(
        "/auth/register",
        json={"email": email, "username": email.split("@")[0], "password": "contrasena1"},
    )
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_crud_and_isolation(client):
    h = _register(client)
    # Sin token -> 401
    assert client.post("/api/v1/me/batches", json={"name": "Kimchi"}).status_code == 401

    created = client.post(
        "/api/v1/me/batches",
        headers=h,
        json={"name": "Kimchi de otoño", "substrate": "col Napa", "method": "lacto",
              "target_days": 14, "temp_c": 18, "ph": 4.2},
    )
    assert created.status_code == 201
    bid = created.json()["id"]

    lst = client.get("/api/v1/me/batches", headers=h).json()
    assert lst["total"] == 1
    assert lst["items"][0]["name"] == "Kimchi de otoño"

    updated = client.put(f"/api/v1/me/batches/{bid}", headers=h, json={"status": "done", "ph": 3.8})
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"
    assert updated.json()["ph"] == 3.8

    assert client.delete(f"/api/v1/me/batches/{bid}", headers=h).status_code == 204
    assert client.get("/api/v1/me/batches", headers=h).json()["total"] == 0


def test_cannot_touch_others_batches(client):
    h1 = _register(client)
    h2 = _register(client)
    bid = client.post(
        "/api/v1/me/batches", headers=h1, json={"name": "Choucroutte"}
    ).json()["id"]
    assert client.put(f"/api/v1/me/batches/{bid}", headers=h2, json={"status": "done"}).status_code == 404
    assert client.delete(f"/api/v1/me/batches/{bid}", headers=h2).status_code == 404


def test_validation(client):
    h = _register(client)
    # target_days mínimo 1 y ph rango válido
    assert client.post("/api/v1/me/batches", headers=h, json={"name": "x", "target_days": 0}).status_code == 422
    assert client.post("/api/v1/me/batches", headers=h, json={"name": "x", "ph": 15}).status_code == 422
    assert client.post("/api/v1/me/batches", headers=h, json={"name": "", "target_days": 2}).status_code == 422


def test_checkpoints_flow(client):
    h = _register(client)
    bid = client.post(
        "/api/v1/me/batches", headers=h, json={"name": "Sauerkraut", "target_days": 21}
    ).json()["id"]

    # checkpoint día 0 y día 5 con pH/temp
    r1 = client.post(
        f"/api/v1/me/batches/{bid}/checkpoints", headers=h,
        json={"day": 0, "ph": 6.1, "temp_c": 20, "notes": "Inicio"},
    )
    r2 = client.post(
        f"/api/v1/me/batches/{bid}/checkpoints", headers=h,
        json={"day": 5, "ph": 4.4, "temp_c": 19},
    )
    assert r1.status_code == 201 and r2.status_code == 201

    lst = client.get(f"/api/v1/me/batches/{bid}/checkpoints", headers=h).json()
    assert lst["total"] == 2
    days = [c["day"] for c in lst["items"]]
    assert days == [0, 5]

    # Otro usuario no puede ver checkpoints de un batch ajeno
    h2 = _register(client)
    assert client.get(f"/api/v1/me/batches/{bid}/checkpoints", headers=h2).status_code == 404

    # checkpoint en batch inexistente
    assert client.post("/api/v1/me/batches/9999/checkpoints", headers=h, json={"day": 1}).status_code == 404