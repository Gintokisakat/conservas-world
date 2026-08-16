import pytest


@pytest.fixture()
def pairings_session(session_factory):
    from ingest.loader import seed_categories, upsert_product

    session = session_factory()
    seed_categories(session)
    records = [
        {
            "name": "Kimchi",
            "description": "Col coreana fermentada.",
            "method": None,
            "fermentation_time": None,
            "aliases": [],
            "countries": [],
            "ingredients": [
                {"name": "cabbage", "category": "vegetal"},
                {"name": "garlic", "category": "aromático"},
                {"name": "chili", "category": "especia"},
            ],
            "categories": ["fermento_lactico"],
            "references": [],
            "source_tag": "test",
        },
        {
            "name": "Sauerkraut",
            "description": "Col fermentada alemana.",
            "method": None,
            "fermentation_time": None,
            "aliases": [],
            "countries": [],
            "ingredients": [
                {"name": "cabbage", "category": "vegetal"},
                {"name": "salt", "category": "mineral"},
            ],
            "categories": ["fermento_lactico"],
            "references": [],
            "source_tag": "test",
        },
        {
            "name": "Gochujang",
            "description": "Pasta coreana picante.",
            "method": None,
            "fermentation_time": None,
            "aliases": [],
            "countries": [],
            "ingredients": [
                {"name": "chili", "category": "especia"},
                {"name": "rice", "category": "cereal"},
                {"name": "soybean", "category": "legumbre"},
            ],
            "categories": ["fermento_koji"],
            "references": [],
            "source_tag": "test",
        },
        {
            "name": "Kombucha",
            "description": "Té fermentado.",
            "method": None,
            "fermentation_time": None,
            "aliases": [],
            "countries": [],
            "ingredients": [
                {"name": "tea", "category": "infusión"},
                {"name": "sugar", "category": "edulcorante"},
            ],
            "categories": ["fermento_acetico"],
            "references": [],
            "source_tag": "test",
        },
    ]
    for record in records:
        upsert_product(session, record)
    session.commit()
    yield session
    session.close()


@pytest.fixture()
def pairings_client(pairings_session, session_factory):
    from app.db.database import get_session
    from app.main import app
    from fastapi.testclient import TestClient

    def override_get_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _product_id(session, name):
    from app.db import models
    from sqlalchemy import select

    return session.execute(
        select(models.Product.id).where(models.Product.name == name)
    ).scalar_one()


def test_pairings_ranked_by_jaccard(pairings_client, pairings_session):
    kimchi = _product_id(pairings_session, "Kimchi")
    resp = pairings_client.get(f"/products/{kimchi}/pairings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["product_name"] == "Kimchi"
    assert data["total"] == 2
    names = [i["name"] for i in data["items"]]
    assert names == ["Sauerkraut", "Gochujang"]
    sauerkraut, gochujang = data["items"]
    assert sauerkraut["shared_ingredients"] == ["cabbage"]
    assert sauerkraut["score"] == 0.25
    assert gochujang["shared_ingredients"] == ["chili"]
    assert gochujang["score"] == 0.2


def test_pairings_excludes_discarded(pairings_client, pairings_session):
    from app.db import models
    from sqlalchemy import select

    cabbage = pairings_session.execute(
        select(models.Ingredient).where(models.Ingredient.name == "cabbage")
    ).scalar_one()
    discarded = models.Product(
        name="Kimchi descartado", status="discarded", source_tag="test"
    )
    pairings_session.add(discarded)
    pairings_session.flush()
    discarded.ingredients.append(cabbage)
    pairings_session.commit()

    kimchi = _product_id(pairings_session, "Kimchi")
    resp = pairings_client.get(f"/products/{kimchi}/pairings")
    assert resp.status_code == 200
    names = [i["name"] for i in resp.json()["items"]]
    assert "Kimchi descartado" not in names
    assert resp.json()["total"] == 2


def test_pairings_no_shared_ingredients(pairings_client, pairings_session):
    kombucha = _product_id(pairings_session, "Kombucha")
    resp = pairings_client.get(f"/products/{kombucha}/pairings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_pairings_min_shared(pairings_client, pairings_session):
    kimchi = _product_id(pairings_session, "Kimchi")
    resp = pairings_client.get(f"/products/{kimchi}/pairings?min_shared=2")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_pairings_not_found(pairings_client, pairings_session):
    resp = pairings_client.get("/products/999999/pairings")
    assert resp.status_code == 404
