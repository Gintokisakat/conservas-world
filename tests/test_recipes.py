"""Tests de recetas comunitarias (4.3): CRUD, votos únicos y filtros."""

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
    email = f"chef_{uuid.uuid4().hex[:10]}@example.com"
    r = client.post(
        "/auth/register",
        json={"email": email, "username": email.split("@")[0], "password": "contrasena1"},
    )
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _payload(**overrides):
    base = {
        "title": "Chucrut de la casa",
        "description": "Receta familiar",
        "steps": ["Rallar", "Salar al 2%", "Fermentar 3 semanas"],
        "ingredients": ["repollo", "sal"],
        "difficulty": "facil",
        "prep_time_min": 40,
    }
    base.update(overrides)
    return base


def test_create_feed_detail(client):
    h = _register(client)
    pid = client.get("/products?page_size=1").json()["items"][0]["id"]
    r = client.post("/recipes", headers=h, json=_payload(product_id=pid))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["mine"] is True and body["author"]["username"]
    assert body["steps"] == ["Rallar", "Salar al 2%", "Fermentar 3 semanas"]
    feed = client.get("/recipes?sort=recent").json()
    assert feed["total"] >= 1 and feed["items"][0]["title"] == "Chucrut de la casa"
    detail = client.get(f"/recipes/{body['id']}").json()
    assert detail["product_id"] == pid


def test_update_and_delete_own_only(client):
    h1 = _register(client)
    h2 = _register(client)
    rid = client.post("/recipes", headers=h1, json=_payload()).json()["id"]
    assert client.put(f"/recipes/{rid}", headers=h2, json=_payload(title="hack")).status_code == 403
    upd = client.put(f"/recipes/{rid}", headers=h1, json=_payload(title="Chucrut v2", difficulty="media"))
    assert upd.status_code == 200 and upd.json()["difficulty"] == "media"
    assert client.delete(f"/recipes/{rid}", headers=h2).status_code == 403
    assert client.delete(f"/recipes/{rid}", headers=h1).status_code == 204
    assert client.get(f"/recipes/{rid}").status_code == 404


def test_vote_once_per_user(client):
    h1 = _register(client)
    h2 = _register(client)
    rid = client.post("/recipes", headers=h1, json=_payload()).json()["id"]
    assert client.post(f"/recipes/{rid}/vote", headers=h2).json()["votes"] == 1
    assert client.post(f"/recipes/{rid}/vote", headers=h2).status_code == 409
    assert client.get(f"/recipes/{rid}").json()["votes"] == 1
    # Unvote
    assert client.delete(f"/recipes/{rid}/vote", headers=h2).json()["voted"] is False
    assert client.get(f"/recipes/{rid}").json()["votes"] == 0


def test_unauth_cannot_create_or_vote(client):
    assert client.post("/recipes", json=_payload()).status_code == 401
    h = _register(client)
    rid = client.post("/recipes", headers=h, json=_payload()).json()["id"]
    assert client.post(f"/recipes/{rid}/vote").status_code == 401


def test_filters_difficulty_and_q(client):
    h = _register(client)
    client.post("/recipes", headers=h, json=_payload(title="Miso casero exprés", difficulty="dificil"))
    client.post("/recipes", headers=h, json=_payload(title="Yogur simple"))
    d = client.get("/recipes?difficulty=dificil").json()["items"]
    assert all(r["difficulty"] == "dificil" for r in d) and len(d) >= 1
    q = client.get("/recipes?q=miso").json()["items"]
    assert any("Miso" in r["title"] for r in q)


def test_invalid_payload_422(client):
    h = _register(client)
    assert client.post("/recipes", headers=h, json=_payload(title="ab")).status_code == 422
    assert client.post("/recipes", headers=h, json=_payload(difficulty="experto")).status_code == 422
    assert client.post("/recipes", headers=h, json=_payload(prep_time_min=-5)).status_code == 422


def test_product_link_404(client):
    h = _register(client)
    assert client.post("/recipes", headers=h, json=_payload(product_id=999999)).status_code == 404


def test_frontend_recipes_integration(client):
    html = client.get("/").text
    assert 'id="recipes-btn"' in html and 'id="recipes-modal"' in html
    js = client.get("/static/app.js").text
    for marker in ["openRecipesModal", "renderRecipesFeed", "renderRecipeForm",
                   "/recipes/", "data-recipe-vote"]:
        assert marker in js, marker