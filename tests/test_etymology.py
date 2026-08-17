"""Tests de etimología (2.9): búsqueda, detalle de producto e i18n."""

from app.main import app
from app.services.etymology import etymology_out, lookup, search_terms
from fastapi.testclient import TestClient

client = TestClient(app)


def test_curated_entries_present():
    for term in ["kimchi", "sauerkraut", "miso", "kombucha", "yogurt", "kefir", "vinagre"]:
        assert lookup(term) is not None


def test_lookup_by_substring():
    assert lookup("chucrut") is not None
    assert lookup("Sauerkraut") is not None
    assert lookup("") is None


def test_search_terms():
    hits = search_terms("miso")
    assert any(h["term"] == "miso" for h in hits)


def test_etymology_out_es_en():
    e = lookup("kimchi")
    es = etymology_out(e, "es")
    en = etymology_out(e, "en")
    assert es["text"] != en["text"]
    assert "coreano" in es["text"].lower() or "coreano" in es["text"]


def test_endpoint_search():
    r = client.get("/etymology/search?q=vinagre")
    assert r.status_code == 200
    assert r.json()["hits"]
    assert r.json()["hits"][0]["term"] in {"vinagre", "escabeche"}


def test_endpoint_product_etymology():
    r = client.get("/products?q=chucrut&page_size=1")
    pid = r.json()["items"][0]["id"]
    e = client.get(f"/products/{pid}/etymology").json()
    assert e is not None
    assert e["term"] == "chucrut"
    assert e["text"]


def test_endpoint_product_etymology_unknown():
    assert client.get("/products/4990/etymology").json() is None


def test_endpoint_404():
    assert client.get("/products/999999/etymology").status_code == 404


def test_etymology_in_public_api():
    assert client.get("/api/v1/etymology/search?q=koji").status_code == 200


def test_frontend_has_etymology_block():
    js = client.get("/static/app.js").text
    assert "etymologyHtml" in js
    assert "/etymology?lang=" in js