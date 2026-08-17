import pytest


@pytest.fixture()
def timer_session(session_factory):
    from ingest.loader import seed_categories, upsert_product

    session = session_factory()
    seed_categories(session)
    records = [
        {
            "name": "Miso",
            "description": "Pasta de soja fermentada japonesa.",
            "method": "fermentación con koji",
            "fermentation_time": "3-24 meses",
            "aliases": [],
            "countries": [],
            "ingredients": [{"name": "soybean", "category": "legumbre"}],
            "categories": ["fermento_koji"],
            "references": [],
            "source_tag": "test",
        },
        {
            "name": "Sauerkraut",
            "description": "Col fermentada alemana.",
            "method": "fermentación láctica",
            "fermentation_time": "2-4 semanas",
            "aliases": [],
            "countries": [],
            "ingredients": [{"name": "cabbage", "category": "vegetal"}],
            "categories": ["fermento_lactico"],
            "references": [],
            "source_tag": "test",
        },
        {
            "name": "Kombucha",
            "description": "Té fermentado.",
            "method": None,
            "fermentation_time": "sin datos",
            "aliases": [],
            "countries": [],
            "ingredients": [{"name": "tea", "category": "infusión"}],
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
def timer_client(timer_session, session_factory):
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


def test_parse_days():
    from app.services.timers import parse_days

    assert parse_days("3-24 meses") == (90, 720)
    assert parse_days("2-4 semanas") == (14, 28)
    assert parse_days("1 día") == (1, 1)
    assert parse_days("6-12 horas") is None
    assert parse_days(None) is None
    assert parse_days("") is None


def test_estimate_days_reference():
    from app.services.timers import estimate_days

    assert estimate_days("3-24 meses", 21) == {"min": 90, "max": 720}
    assert estimate_days("2-4 semanas", 21) == {"min": 14, "max": 28}


def test_estimate_days_q10_frio_mas_lento():
    from app.services.timers import estimate_days

    # A 11 °C (10 °C menos) el doble de días.
    assert estimate_days("2-4 semanas", 11) == {"min": 28, "max": 56}


def test_estimate_days_sin_datos():
    from app.services.timers import estimate_days

    assert estimate_days(None, 21) == {"min": None, "max": None}


def test_timer_endpoint(timer_client, timer_session):
    miso = _product_id(timer_session, "Miso")
    resp = timer_client.get(f"/timers/{miso}?temp_c=21")
    assert resp.status_code == 200
    data = resp.json()
    assert data["product_name"] == "Miso"
    assert data["fermentation_time"] == "3-24 meses"
    assert data["estimated_days"] == {"min": 90, "max": 720}
    assert data["model"].startswith("Q10")


def test_timer_endpoint_ajuste_temperatura(timer_client, timer_session):
    miso = _product_id(timer_session, "Miso")
    resp = timer_client.get(f"/timers/{miso}?temp_c=11")
    assert resp.status_code == 200
    assert resp.json()["estimated_days"] == {"min": 180, "max": 1440}


def test_timer_endpoint_sin_rango(timer_client, timer_session):
    kombucha = _product_id(timer_session, "Kombucha")
    resp = timer_client.get(f"/timers/{kombucha}?temp_c=21")
    assert resp.status_code == 200
    assert resp.json()["estimated_days"] == {"min": None, "max": None}


def test_timer_endpoint_not_found(timer_client, timer_session):
    resp = timer_client.get("/timers/999999")
    assert resp.status_code == 404