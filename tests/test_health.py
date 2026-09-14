"""Roadmap 5.4 — monitoreo: /api/health con uptime y métricas por ruta."""

from app.api import public as public_api


def test_health_basico(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"
    assert body["version"]
    assert body["uptime_seconds"] >= 0
    assert body["requests_total"] >= 0
    assert isinstance(body["requests_by_path"], list)


def test_health_registra_rutas_visitadas(client):
    try:
        public_api.reset_monitoring()
        client.get("/api/v1/products?limit=1")
        client.get("/api/v1/categories")
        r = client.get("/api/health").json()
        paths = {row["path"] for row in r["requests_by_path"]}
        assert "/api/v1/products" in paths
        assert "/api/v1/categories" in paths
        assert r["requests_total"] >= 2
        for row in r["requests_by_path"]:
            assert row["count"] >= 1
            assert row["p95_ms"] >= 0
            assert row["avg_ms"] >= 0
    finally:
        public_api.reset_monitoring()


def test_health_no_rompe_sin_muestras(client):
    try:
        public_api.reset_monitoring()
        r = client.get("/api/health").json()
        assert r["requests_total"] == 0
        assert r["requests_by_path"] == []
    finally:
        public_api.reset_monitoring()


def test_access_log_resetea_variables():
    assert callable(public_api.record_request)
    try:
        public_api.record_request("/api/v1/x", 12.5)
        assert len(public_api._by_path["/api/v1/x"]) == 1
    finally:
        public_api.reset_monitoring()