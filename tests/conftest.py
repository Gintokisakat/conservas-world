import os

os.environ["CONSERVAS_WARMUP"] = "0"

import pytest
from app.db import models  # noqa: F401, E402
from app.db.database import Base, get_session  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

TEST_DB_URL = "sqlite://"


@pytest.fixture()
def session_factory(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path}/test.db", connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)
    yield TestingSessionLocal
    engine.dispose()


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    try:
        _seed(session)
        session.commit()
    finally:
        session.close()

    session = session_factory()
    yield session
    session.close()


@pytest.fixture()
def client(session_factory):
    TestingSessionLocal = session_factory

    def override_get_session():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session

    session = TestingSessionLocal()
    try:
        _seed(session)
        session.commit()
    finally:
        session.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _seed(session):
    from ingest.loader import seed_categories, seed_country_coords, upsert_product
    from ingest.sources.glossary import seed_glossary

    seed_categories(session)
    seed_country_coords(session)
    records = [
        {
            "name": "Miso",
            "description": "Pasta de soja fermentada japonesa",
            "method": "fermentación con koji",
            "fermentation_time": "3-24 meses",
            "aliases": [],
            "countries": [
                {
                    "name": "Japan",
                    "iso2": "JP",
                    "iso3": "JPN",
                    "continent": "Asia",
                }
            ],
            "ingredients": [{"name": "soybean", "category": "legumbre"}, {"name": "rice", "category": "cereal"}],
            "categories": ["fermento_koji"],
            "references": [
                {
                    "title": "Test reference",
                    "ref_type": "web",
                    "url": "https://example.org",
                    "doi": None,
                }
            ],
            "source_tag": "test",
        },
        {
            "name": "Sauerkraut",
            "description": "Col fermentada alemana",
            "method": "fermentación láctica",
            "fermentation_time": "2-4 semanas",
            "aliases": [{"name": "chucrut", "language": "es"}],
            "countries": [
                {
                    "name": "Germany",
                    "iso2": "DE",
                    "iso3": "DEU",
                    "continent": "Europe",
                }
            ],
            "ingredients": [{"name": "cabbage", "category": "vegetal"}],
            "categories": ["fermento_lactico"],
            "references": [],
            "source_tag": "test",
        },
    ]
    for record in records:
        upsert_product(session, record)
    seed_country_coords(session)
    seed_glossary(session)
