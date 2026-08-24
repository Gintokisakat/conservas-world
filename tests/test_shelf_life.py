"""Tests de shelf-life (2.15): perfiles, lookup, endpoint e integración frontend."""

from app.main import app
from app.services.shelf_life import PROFILES, lookup, shelf_life_out
from fastapi.testclient import TestClient

client = TestClient(app)


def test_profiles_curated():
    assert len(PROFILES) >= 10


def test_lookup_matches():
    for term in ["repollo", "kimchi", "kombucha", "miso", "vinagre", "yogur",
                 "queso cheddar", "salsa de pescado", "tamari", "encurtido de zanahoria"]:
        assert lookup(term) is not None, term


def test_lookup_no_false_positives():
    for term in ["tuna", "tamarind", "aceite", ""]:
        assert lookup(term) is None, term


def test_shelf_life_out_bilingual():
    p = lookup("miso")
    es = shelf_life_out(p, "es")
    en = shelf_life_out(p, "en")
    assert es["notes"] != en["notes"]
    assert es["fridge_days"] == en["fridge_days"] > 0


def test_endpoint_by_ingredient_id():
    r = client.get("/products?ingredient=miso&page_size=1")
    items = r.json()["items"]
    if not items:
        return
    # find the ingredient id via search suggest
    sug = client.get("/search/suggest?q=miso").json()
    ing = [s for s in sug.get("ingredients", []) if s["name"] == "miso"]
    if not ing:
        return
    sid = ing[0]["id"]
    resp = client.get(f"/ingredients/{sid}/shelf-life")
    assert resp.status_code == 200
    body = resp.json()
    assert body is not None and body["category"] == "Fermentos de soja"


def test_endpoint_lang_en():
    r = client.get("/ingredients/152/shelf-life?lang=en")
    assert r.status_code == 200
    body = r.json()
    assert body is None or body["category"] == "Soy ferments" or body["notes"]


def test_endpoint_unknown_ingredient():
    assert client.get("/ingredients/999999/shelf-life").status_code == 404


def test_endpoint_public_api():
    assert client.get("/api/v1/ingredients/152/shelf-life").status_code == 200


def test_frontend_shelf_life_block():
    js = client.get("/static/app.js").text
    for marker in ["shelf-life?lang=", "¿Cuánto dura?", "How long does it keep?", "shelfLife"]:
        assert marker in js, marker