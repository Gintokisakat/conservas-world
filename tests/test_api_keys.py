"""Tests de API keys para acceso programático (roadmap 5.5)."""
import pytest
from app.db import models
from app.main import app
from app.services.auth import generate_api_key, hash_api_key
from sqlalchemy import select


@pytest.fixture()
def auth_client(client):
    """Registra un usuario y devuelve (client, access_token)."""
    resp = client.post(
        "/auth/register",
        json={"email": "keys@example.com", "username": "keyuser", "password": "hunter2hunter2"},
    )
    assert resp.status_code == 201, resp.text
    return client, resp.json()["access_token"]


def test_generate_api_key_is_unique_and_prefixed():
    keys = {generate_api_key() for _ in range(50)}
    assert len(keys) == 50
    assert all(k.startswith("cdm_") for k in keys)
    assert all(len(k) >= 40 for k in keys)


def test_hash_api_key_is_stable_and_hides_plaintext():
    key = generate_api_key()
    digest = hash_api_key(key)
    assert digest == hash_api_key(key)
    assert key not in digest
    assert len(digest) == 64


def test_api_key_lifecycle(auth_client):
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token}"}

    # Crear
    resp = client.post("/auth/api-keys", json={"name": "CI script"}, headers=headers)
    assert resp.status_code == 201, resp.text
    created = resp.json()
    plaintext = created["key"]
    assert plaintext.startswith("cdm_")
    assert created["name"] == "CI script"
    assert created["active"] is True
    key_id = created["id"]

    # Listar: nunca debe devolver la clave en claro
    resp = client.get("/auth/api-keys", headers=headers)
    assert resp.status_code == 200
    listing = resp.json()["items"]
    assert len(listing) == 1
    assert "key" not in listing[0]
    assert plaintext not in resp.text

    # La base almacena solo el hash
    stored = listing[0]["id"]
    assert stored == key_id

    # Revocar
    resp = client.delete(f"/auth/api-keys/{key_id}", headers=headers)
    assert resp.status_code == 204
    resp = client.get("/auth/api-keys", headers=headers)
    assert resp.json()["items"][0]["active"] is False


def test_api_key_requires_auth(auth_client):
    client, _ = auth_client
    assert client.get("/auth/api-keys").status_code == 401
    assert client.post("/auth/api-keys", json={"name": "x"}).status_code == 401
    assert client.delete("/auth/api-keys/1").status_code == 401


def test_revoke_unknown_key_returns_404(auth_client):
    client, token = auth_client
    resp = client.delete(
        "/auth/api-keys/9999", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


def test_cannot_revoke_another_users_key(auth_client, session_factory):
    client, token = auth_client
    mine = client.post(
        "/auth/api-keys", json={"name": "mine"}, headers={"Authorization": f"Bearer {token}"}
    ).json()

    # Otro usuario, con su propia key
    other = client.post(
        "/auth/register",
        json={"email": "other@example.com", "username": "other", "password": "hunter2hunter2"},
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other}"}
    other_key = client.post(
        "/auth/api-keys", json={"name": "theirs"}, headers=other_headers
    ).json()

    # El primero intenta revocar la key del segundo
    resp = client.delete(f"/auth/api-keys/{other_key['id']}", headers=headers_of(token))
    assert resp.status_code == 404

    # Y tampoco puede verla en su listado
    listing = client.get("/auth/api-keys", headers=headers_of(token)).json()["items"]
    assert [k["id"] for k in listing] == [mine["id"]]

    # Ambas siguen activas
    with session_factory() as session:
        assert session.query(models.ApiKey).count() == 2


def headers_of(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_api_key_resolves_user(client, auth_client, session_factory):
    """El header X-API-Key debe resolver al usuario dueño de la key."""
    _, token = auth_client
    plaintext = client.post(
        "/auth/api-keys",
        json={"name": "integration"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["key"]

    from app.api.auth import get_api_key_user
    from app.db.database import get_session

    session = session_factory()

    def override():
        yield session

    app.dependency_overrides[get_session] = override
    try:
        user = get_api_key_user(x_api_key=plaintext, session=session)
        assert user is not None
        assert user.email == "keys@example.com"
        # last_used_at se actualiza en cada uso
        record = session.execute(
            select(models.ApiKey).where(models.ApiKey.user_id == user.id)
        ).scalar_one()
        assert record.last_used_at is not None

        assert get_api_key_user(x_api_key="cdm_invalida", session=session) is None
        assert get_api_key_user(x_api_key=None, session=session) is None
    finally:
        app.dependency_overrides.pop(get_session, None)
        session.close()


def test_revoked_key_no_longer_resolves(client, auth_client, session_factory):
    _, token = auth_client
    created = client.post(
        "/auth/api-keys",
        json={"name": "temp"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    from app.api.auth import get_api_key_user

    session = session_factory()
    try:
        assert get_api_key_user(x_api_key=created["key"], session=session) is not None
        client.delete(
            f"/auth/api-keys/{created['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_api_key_user(x_api_key=created["key"], session=session) is None
    finally:
        session.close()


def test_api_key_name_validation(auth_client):
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/auth/api-keys", json={"name": ""}, headers=headers).status_code == 422
    assert (
        client.post("/auth/api-keys", json={"name": "x" * 200}, headers=headers).status_code
        == 422
    )
