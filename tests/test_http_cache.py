"""Tests de caché HTTP condicional (roadmap 5.3): Cache-Control + ETag/304."""
import hashlib

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture()
def c(client):
    return client


def test_product_detail_has_public_cache_and_etag(c):
    r = c.get("/products/1")
    assert r.status_code == 200
    assert "public" in r.headers.get("Cache-Control", "")
    assert r.headers.get("ETag", "").startswith('"')


def test_if_none_match_returns_304(c):
    first = c.get("/products/1")
    etag = first.headers["ETag"]
    second = c.get("/products/1", headers={"If-None-Match": etag})
    assert second.status_code == 304
    assert second.headers["ETag"] == etag
    # Un 304 no debe llevar cuerpo
    assert second.content == b""


def test_stale_etag_returns_full_body(c):
    r = c.get("/products/1", headers={"If-None-Match": '"deadbeefnotarealetag"'})
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_wildcard_if_none_match(c):
    r = c.get("/products/1", headers={"If-None-Match": "*"})
    assert r.status_code == 304


def test_etag_list_of_multiple(c):
    etag = c.get("/products/1").headers["ETag"]
    r = c.get("/products/1", headers={"If-None-Match": f'"other", {etag}'})
    assert r.status_code == 304


def test_etag_is_hash_of_body(c):
    """El ETag se deriva del cuerpo: mismo cuerpo, mismo ETag."""
    r = c.get("/products/1?lang=es")
    expected = '"' + hashlib.sha256(r.content).hexdigest()[:32] + '"'
    assert r.headers["ETag"] == expected


def test_etag_varies_with_content(c):
    """Productos distintos no pueden compartir ETag."""
    products = c.get("/products?page_size=5").json()["items"]
    etags = {
        c.get(f"/products/{p['id']}").headers["ETag"] for p in products[:3]
    }
    assert len(etags) == len(products[:3])


def test_etag_stable_between_requests(c):
    a = c.get("/products/1").headers["ETag"]
    b = c.get("/products/1").headers["ETag"]
    assert a == b


def test_auth_responses_are_not_cached(c):
    r = c.get("/auth/me")
    assert r.status_code == 401
    assert "no-store" in r.headers.get("Cache-Control", "")
    assert "ETag" not in r.headers


def test_error_responses_have_no_etag(c):
    r = c.get("/products/999999")
    assert r.status_code in (404, 400)
    assert "ETag" not in r.headers


def test_duplicate_routes_share_etag(c):
    """Las rutas registradas en / y /api/v1 deben servir la misma versión."""
    root = c.get("/products/1")
    v1 = c.get("/api/v1/products/1")
    assert root.status_code == v1.status_code == 200
    assert root.headers["ETag"] == v1.headers["ETag"]


def test_static_cache_control_present(c):
    r = c.get("/static/app.js")
    assert r.status_code == 200
    assert "Cache-Control" in r.headers


def test_stats_cached_5min(c):
    r = c.get("/stats")
    assert r.status_code == 200
    assert "max-age=300" in r.headers.get("Cache-Control", "")
