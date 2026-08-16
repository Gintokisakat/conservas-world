import pytest


@pytest.fixture()
def dairy_seed(session_factory):
    from ingest.loader import seed_categories, upsert_product
    from ingest.sources.glossary import seed_glossary

    session = session_factory()
    seed_categories(session)
    records = [
        {
            "name": "Gorgonzola",
            "description": "Queso tradicional de leche de vaca de Italia.",
            "method": None,
            "fermentation_time": None,
            "aliases": [],
            "countries": [
                {"name": "Italy", "iso2": "IT", "iso3": "ITA", "continent": "Europe"}
            ],
            "ingredients": [{"name": "milk", "category": "lacteo"}],
            "categories": ["fermento_lactico"],
            "references": [],
            "source_tag": "fdfdb",
            "_dairy": {
                "name": "Gorgonzola",
                "classification": "cheese",
                "country": "Italy",
                "region": "Lombardy",
                "milk_type": "vaca",
                "treatment": None,
                "ripening": "blando",
                "microbiota": ["Penicillium roqueforti", "Geotrichum candidum"],
                "geographical_indication": True,
                "characteristics": "a soft cow's milk cheese",
            },
        },
        {
            "name": "Mursik",
            "description": "Leche fermentada tradicional de Kenia.",
            "method": None,
            "fermentation_time": None,
            "aliases": [],
            "countries": [
                {"name": "Kenya", "iso2": "KE", "iso3": "KEN", "continent": "Africa"}
            ],
            "ingredients": [{"name": "milk", "category": "lacteo"}],
            "categories": ["fermento_lactico"],
            "references": [],
            "source_tag": "fdfdb",
            "_dairy": {
                "name": "Mursik",
                "classification": "fermented milk",
                "country": "Kenya",
                "region": "",
                "milk_type": None,
                "treatment": None,
                "ripening": None,
                "microbiota": [],
                "geographical_indication": False,
                "characteristics": None,
            },
        },
    ]
    for record in records:
        upsert_product(session, record)
    import json as _json

    from app.db import models
    from sqlalchemy import select

    for record in records:
        product = session.execute(
            select(models.Product).where(models.Product.name == record["name"])
        ).scalar_one()
        payload = dict(record["_dairy"])
        microbiota = payload.pop("microbiota", [])
        payload["microbiota_json"] = (
            _json.dumps(microbiota, ensure_ascii=False) if microbiota else None
        )
        session.add(models.DairyFerment(product_id=product.id, **payload))
    seed_glossary(session)
    session.commit()
    session.close()


def test_fdfdb_parser_rows():
    from ingest.sources.fdfdb import _load_rows

    rows = _load_rows()
    assert len(rows) > 1000
    cheese = next(r for r in rows if r["name"] == "Abondance")
    assert cheese["_dairy"]["classification"] == "cheese"
    assert cheese["_dairy"]["country"] == "France"
    assert cheese["_dairy"]["geographical_indication"] is True
    assert "milk" in {i["name"] for i in cheese["ingredients"]}
    assert cheese["categories"] == ["fermento_lactico"]
    assert cheese["source_tag"] == "fdfdb"


def test_fdfdb_parser_gi_subset():
    from ingest.sources.fdfdb import _load_rows

    rows = _load_rows()
    gi = [r for r in rows if r["_dairy"]["geographical_indication"]]
    assert 100 <= len(gi) <= 150


def test_api_dairy_endpoint(client, dairy_seed):
    resp = client.get("/products/dairy")
    assert resp.status_code == 200
    data = resp.json()
    names = {item["name"] for item in data["items"]}
    assert names == {"Gorgonzola", "Mursik"}


def test_api_dairy_gi_filter(client, dairy_seed):
    resp = client.get("/products/dairy?gi=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Gorgonzola"
    assert data["items"][0]["geographical_indication"] is True


def test_api_dairy_classification(client, dairy_seed):
    resp = client.get("/products/dairy?classification=fermented%20milk")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Mursik"


def test_api_product_gi_filter(client, dairy_seed):
    resp = client.get("/products?gi=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Gorgonzola"


def test_api_product_detail_dairy(client, dairy_seed):
    resp = client.get("/products/dairy?classification=cheese")
    product_id = resp.json()["items"][0]["id"]
    detail = client.get(f"/products/{product_id}")
    assert detail.status_code == 200
    data = detail.json()
    assert data["dairy"]["classification"] == "cheese"
    assert data["dairy"]["milk_type"] == "vaca"
    assert data["dairy"]["geographical_indication"] is True
    assert data["dairy"]["microbiota"] == ["Penicillium roqueforti", "Geotrichum candidum"]


def test_export_includes_gi(client, dairy_seed):
    resp = client.get("/products/dairy?classification=cheese")
    product_id = resp.json()["items"][0]["id"]
    csv = client.get(f"/products/{product_id}/export?format=csv")
    assert csv.status_code == 200
    assert "Indicación geográfica" in csv.text
    assert "Sí" in csv.text
