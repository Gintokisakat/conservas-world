"""Tests de la API pública (3.9): /api, /api/health, /api/v1 y rate-limit."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_api_root_lists_endpoints():
    r = client.get("/api")
    assert r.status_code == 200
    d = r.json()
    assert d["version"] == "v1"
    paths = {e["path"] for e in d["endpoints"]}
    assert "/api/v1/products" in paths
    assert "/api/v1/timers/{product_id}" in paths
    assert "/api/v1/glossary" in paths


def test_api_root_with_trailing_slash():
    assert client.get("/api/").status_code == 200


def test_api_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["db"] == "ok"


def test_api_v1_products():
    r = client.get("/api/v1/products?page_size=3")
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 3


def test_api_v1_product_detail():
    r = client.get("/api/v1/products/84")
    assert r.status_code == 200
    assert r.json()["name"] == "Burrata"


def test_api_v1_pairings():
    r = client.get("/api/v1/products/84/pairings")
    assert r.status_code == 200
    assert "items" in r.json()


def test_api_v1_timer():
    r = client.get("/api/v1/timers/84?temp_c=21")
    assert r.status_code == 200
    assert r.json()["estimated_days"] == {"min": 7, "max": 21}


def test_api_rate_limit_headers():
    r = client.get("/api/health")
    assert r.headers["X-RateLimit-Limit"] == "120"
    assert int(r.headers["X-RateLimit-Remaining"]) >= 0
    assert int(r.headers["X-RateLimit-Reset"]) >= 0


def test_rate_limit_exhaustion_returns_429():
    from app.api.public import RATE_LIMIT_REQUESTS, check_rate_limit

    remaining = check_rate_limit("test-client")
    assert remaining == RATE_LIMIT_REQUESTS - 1


def test_public_api_does_not_break_frontend():
    r = client.get("/")
    assert r.status_code == 200