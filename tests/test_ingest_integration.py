"""Tests de integración para el pipeline de ingesta."""
import pytest
from app.db import models
from app.db.database import Base, get_session
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def ingest_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path}/test_ingest.db", connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)
    session = TestingSessionLocal()
    yield session
    session.close()
    engine.dispose()


def test_upsert_product_creates_product(ingest_session):
    from ingest.loader import upsert_product, seed_categories, seed_country_coords

    seed_categories(ingest_session)
    seed_country_coords(ingest_session)

    record = {
        "name": "Test Ferment",
        "description": "A test fermented product",
        "method": "lactic fermentation",
        "fermentation_time": "7-14 days",
        "aliases": [{"name": "Test Alias", "language": "en"}],
        "countries": [{"name": "Japan", "iso2": "JP", "iso3": "JPN", "continent": "Asia"}],
        "ingredients": [{"name": "soybean", "category": "legume"}],
        "categories": ["fermento_koji"],
        "references": [],
        "source_tag": "test",
    }
    product = upsert_product(ingest_session, record)
    assert product.id is not None
    assert product.name == "Test Ferment"
    assert len(product.aliases) == 1
    assert len(product.countries) == 1
    assert len(product.ingredients) == 1


def test_upsert_product_deduplication(ingest_session):
    from ingest.loader import upsert_product, seed_categories, seed_country_coords

    seed_categories(ingest_session)
    seed_country_coords(ingest_session)

    record = {
        "name": "Test Ferment",
        "description": "A test fermented product",
        "method": "lactic fermentation",
        "fermentation_time": "7-14 days",
        "aliases": [],
        "countries": [{"name": "Japan", "iso2": "JP", "iso3": "JPN", "continent": "Asia"}],
        "ingredients": [{"name": "soybean", "category": "legume"}],
        "categories": ["fermento_koji"],
        "references": [],
        "source_tag": "test",
    }
    product1 = upsert_product(ingest_session, record)
    product2 = upsert_product(ingest_session, record)
    assert product1.id == product2.id


def test_normalize_name():
    from ingest.normalize import normalize_name

    assert normalize_name("  Kimchi  ") == "kimchi"
    assert normalize_name("Sauerkraut") == "sauerkraut"
    assert normalize_name("Chucrut") == "chucrut"


def test_match_ingredients():
    from ingest.ingredients import match_ingredients

    hits = match_ingredients("cabbage")
    assert len(hits) > 0
    assert any(h["name"] == "cabbage" for h in hits)


def test_semantic_search_empty_db(ingest_session):
    from app.services.semantic import semantic_search

    hits = semantic_search(ingest_session, "kimchi", limit=5)
    assert hits == []


def test_safety_assessment(ingest_session):
    from app.services.safety import safety_assessment
    from ingest.loader import upsert_product, seed_categories, seed_country_coords

    seed_categories(ingest_session)
    seed_country_coords(ingest_session)

    record = {
        "name": "Test Kimchi",
        "description": "Spicy fermented cabbage",
        "method": "lactic fermentation",
        "fermentation_time": "1-2 weeks",
        "aliases": [],
        "countries": [{"name": "South Korea", "iso2": "KR", "iso3": "KOR", "continent": "Asia"}],
        "ingredients": [{"name": "cabbage", "category": "vegetable"}],
        "categories": ["fermento_lactico"],
        "references": [],
        "source_tag": "test",
    }
    product = upsert_product(ingest_session, record)
    assessment = safety_assessment(product, "es")
    assert assessment is not None
    assert hasattr(assessment, "ph_min")
    assert hasattr(assessment, "ph_max")
