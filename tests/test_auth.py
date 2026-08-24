"""Tests de autenticación (4.1): registro, login, tokens, preferencias."""

import uuid

import pytest
from app.db.database import Base, get_session
from app.main import app
from app.services.auth import hash_password, verify_password
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def client():
    """Cliente con get_session sobre BD de prueba (no toca build.db real)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)

    session = TestingSessionLocal()
    from app.db import models

    session.add(models.Product(name="Kimchi", status="imported"))
    session.commit()
    session.close()

    def _override():
        s = TestingSessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_session] = _override
    yield TestClient(app)
    app.dependency_overrides.pop(get_session, None)
    engine.dispose()


@pytest.fixture()
def email():
    return f"user_{uuid.uuid4().hex[:10]}@example.com"


@pytest.fixture()
def tokens(client, email):
    r = client.post(
        "/auth/register",
        json={"email": email, "username": email.split("@")[0], "password": "contrasena1"},
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_password_hash_roundtrip():
    stored = hash_password("mi-clave-segura")
    assert stored.startswith("scrypt$")
    assert verify_password("mi-clave-segura", stored)
    assert not verify_password("otra-clave", stored)
    assert not verify_password("x", "basura")


def test_register_and_login(client, email, tokens):
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"] and tokens["refresh_token"]
    r = client.post("/auth/login", json={"email": email, "password": "contrasena1"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_register_duplicate_conflict(client, email, tokens):
    r = client.post(
        "/auth/register",
        json={"email": email.upper(), "username": "other_" + email.split("@")[0], "password": "contrasena1"},
    )
    assert r.status_code == 409


def test_register_invalid_payload(client):
    assert client.post("/auth/register", json={"email": "no-email", "username": "x", "password": "contrasena1"}).status_code in {409, 422}
    assert client.post("/auth/register", json={"email": "a@b.com", "username": "ab", "password": "contrasena1"}).status_code == 422
    assert client.post("/auth/register", json={"email": "a@b.com", "username": "abc", "password": "corta"}).status_code == 422


def test_login_wrong_password(client, email, tokens):
    r = client.post("/auth/login", json={"email": email, "password": "incorrecta1"})
    assert r.status_code == 401


def test_me_roundtrip(client, email, tokens):
    h = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = client.get("/auth/me", headers=h).json()
    assert me["email"] == email
    assert me["preferences"] == {}


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer invalido"}).status_code == 401


def test_refresh_flow(client, email, tokens):
    r = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    new_pair = r.json()
    # El access nuevo debe funcionar.
    h = {"Authorization": f"Bearer {new_pair['access_token']}"}
    assert client.get("/auth/me", headers=h).status_code == 200


def test_refresh_rejects_access_token(client, tokens):
    r = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert r.status_code == 401


def test_preferences_update_and_read(client, email, tokens):
    h = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = client.put("/auth/me/preferences", headers=h, json={"preferences": {"lang": "en", "region": "eu"}})
    assert r.status_code == 200
    assert r.json()["preferences"] == {"lang": "en", "region": "eu"}
    assert client.get("/auth/me", headers=h).json()["preferences"] == {"lang": "en", "region": "eu"}


def test_auth_rate_limit(client, email):
    for _ in range(12):
        client.post("/auth/register", json={"email": f"x{uuid.uuid4().hex[:6]}@e.com", "username": uuid.uuid4().hex[:8], "password": "contrasena1"})
    r = client.post("/auth/register", json={"email": email, "username": email.split("@")[0], "password": "contrasena1"})
    assert r.status_code == 429


def test_frontend_auth_integration(client):
    html = client.get("/").text
    assert 'id="auth-modal"' in html and 'id="auth-area"' in html
    js = client.get("/static/app.js").text
    for marker in ["doLogin", "doRegister", "loadSession", "pantry_auth_token",
                   "/auth/refresh", "renderAuthArea"]:
        assert marker in js, marker