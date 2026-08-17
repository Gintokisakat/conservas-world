"""Tests de búsqueda semántica (3.5): tokenización, índice TF-IDF y endpoint /search/semantic."""

from app.main import app
from app.services.semantic import tokenize
from fastapi.testclient import TestClient

client = TestClient(app)


def test_tokenize_lowercases_and_filters_stopwords():
    assert tokenize("Kimchi de Repollo Picante") == ["kimchi", "repollo", "picante"]
    assert tokenize("Algo Tradicional") == ["algo"]


def test_semantic_endpoint_returns_hits():
    r = client.get("/search/semantic?q=algo picante fermentado")
    assert r.status_code == 200
    d = r.json()
    assert d["query"] == "algo picante fermentado"
    assert len(d["hits"]) > 0
    assert d["hits"][0]["score"] > 0


def test_semantic_endpoint_ranks_relevant_products():
    r = client.get("/search/semantic?q=queso leche curado")
    names = [h["name"] for h in r.json()["hits"]]
    assert any("queso" in n.lower() or "cheese" in n.lower() for n in names)


def test_semantic_empty_query():
    r = client.get("/search/semantic?q=")
    assert r.json()["hits"] == []


def test_semantic_limit():
    r = client.get("/search/semantic?q=picante&limit=5")
    assert len(r.json()["hits"]) <= 5


def test_semantic_available_in_public_api():
    assert client.get("/api/v1/search/semantic?q=miso").status_code == 200


def test_frontend_includes_semantic_toggle():
    page = client.get("/").text
    assert 'id="semantic"' in page
    js = client.get("/static/app.js").text
    assert "searchSemantic" in js
    assert "renderSemanticResults" in js