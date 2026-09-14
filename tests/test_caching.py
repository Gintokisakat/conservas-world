"""Roadmap 5.3 — cabeceras Cache-Control en endpoints de lectura."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_categories_cache_public_1h():
    r = client.get("/api/v1/categories")
    assert r.status_code == 200
    assert r.headers["Cache-Control"] == "public, max-age=3600"


def test_products_list_cache_public_1h():
    r = client.get("/api/v1/products")
    assert r.status_code == 200
    assert r.headers["Cache-Control"] == "public, max-age=3600"


def test_products_detail_cache_public_1h():
    r = client.get("/products/1")
    if r.status_code == 200:
        assert r.headers["Cache-Control"] == "public, max-age=3600"


def test_stats_cache_short():
    r = client.get("/stats")
    assert r.status_code == 200
    assert r.headers["Cache-Control"] == "public, max-age=300"


def test_random_never_cached():
    r = client.get("/products/random")
    assert r.status_code in (200, 404)
    assert "no-store" in r.headers["Cache-Control"]


def test_search_suggest_cache_short():
    r = client.get("/search/suggest?q=tempeh")
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        assert r.headers["Cache-Control"] == "public, max-age=60"


def test_private_me_not_public_cached():
    r = client.get("/api/v1/me/batches")
    assert r.status_code in (200, 401, 403)
    assert r.headers["Cache-Control"] == "private, no-store"


def test_index_no_cache():
    r = client.get("/")
    assert r.status_code == 200
    assert r.headers["Cache-Control"] == "no-cache"


def test_route_set_header_is_respected():
    """Endpoints que ya fijan su propio Cache-Control no se sobrescriben."""
    r = client.get("/api/v1/timeline")
    assert r.status_code == 200
    assert r.headers["Cache-Control"] == "public, max-age=86400"


def test_post_not_cached():
    r = client.post("/auth/login", json={"email": "x@y.z", "password": "nope"})
    assert "Cache-Control" not in r.headers