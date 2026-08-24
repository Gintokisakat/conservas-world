"""Tests de reseñas (4.2): CRUD, permisos, promedio y moderación."""

import uuid

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture()
def client(session_factory):
    """Reutiliza el patrón de conftest: BD de prueba sembrada + override."""
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


def _first_product_id(client):
    return client.get("/products?page_size=1").json()["items"][0]["id"]


def _register(client):
    email = f"rev_{uuid.uuid4().hex[:10]}@example.com"
    r = client.post(
        "/auth/register",
        json={"email": email, "username": email.split("@")[0], "password": "contrasena1"},
    )
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_create_and_list_with_average(client):
    h1 = _register(client)
    h2 = _register(client)
    pid = _first_product_id(client)
    r1 = client.post(f"/products/{pid}/reviews", headers=h1, json={"rating": 5, "text": "Top"})
    r2 = client.post(f"/products/{pid}/reviews", headers=h2, json={"rating": 3})
    assert r1.status_code == 201 and r2.status_code == 201
    out = client.get(f"/products/{pid}/reviews").json()
    assert out["total"] == 2
    assert out["average"] == 4.0
    assert {i["rating"] for i in out["items"]} == {5, 3}


def test_duplicate_review_conflict(client):
    h = _register(client)
    assert client.post(f"/products/{_first_product_id(client)}/reviews", headers=h, json={"rating": 4}).status_code == 201
    assert client.post(f"/products/{_first_product_id(client)}/reviews", headers=h, json={"rating": 5}).status_code == 409


def test_unauthenticated_cannot_review(client):
    assert client.post(f"/products/{_first_product_id(client)}/reviews", json={"rating": 5}).status_code == 401


def test_invalid_rating_422(client):
    h = _register(client)
    for bad in (0, 6, -1):
        assert client.post(f"/products/{_first_product_id(client)}/reviews", headers=h, json={"rating": bad}).status_code == 422


def test_update_own_review_only(client):
    h1 = _register(client)
    h2 = _register(client)
    PID = _first_product_id(client)
    rid = client.post(f"/products/{PID}/reviews", headers=h1, json={"rating": 4}).json()["id"]
    # Otro usuario no puede editar ni borrar.
    assert client.put(f"/reviews/{rid}", headers=h2, json={"rating": 1}).status_code == 403
    assert client.delete(f"/reviews/{rid}", headers=h2).status_code == 403
    # El dueño sí.
    upd = client.put(f"/reviews/{rid}", headers=h1, json={"rating": 2, "text": "meh"})
    assert upd.status_code == 200 and upd.json()["rating"] == 2
    assert client.delete(f"/reviews/{rid}", headers=h1).status_code == 204
    assert client.get(f"/products/{PID}/reviews").json()["total"] == 0


def test_flag_hides_from_list(client):
    h1 = _register(client)
    h2 = _register(client)
    PID = _first_product_id(client)
    rid = client.post(f"/products/{PID}/reviews", headers=h1, json={"rating": 1, "text": "spam"}).json()["id"]
    assert client.post(f"/reviews/{rid}/flag", headers=h2).status_code == 204
    items = client.get(f"/products/{PID}/reviews").json()["items"]
    assert all(i["id"] != rid for i in items)


def test_product_404(client):
    h = _register(client)
    missing = 999999
    assert client.post(f"/products/{missing}/reviews", headers=h, json={"rating": 5}).status_code == 404


def test_mine_flag_marks_own_reviews(client):
    h1 = _register(client)
    h2 = _register(client)
    PID = _first_product_id(client)
    client.post(f"/products/{PID}/reviews", headers=h1, json={"rating": 5, "text": "mía"})
    anon = client.get(f"/products/{PID}/reviews").json()["items"]
    assert all(i["mine"] is False for i in anon)
    own = client.get(f"/products/{PID}/reviews", headers=h1).json()["items"]
    assert [i["mine"] for i in own] == [True]
    other = client.get(f"/products/{PID}/reviews", headers=h2).json()["items"]
    assert [i["mine"] for i in other] == [False]


def test_frontend_reviews_integration(client):
    js = client.get("/static/app.js").text
    for marker in ["loadProductReviews", "apiSend", "review-stars", "/reviews/", "starsText"]:
        assert marker in js, marker