"""Tests de cachés por fingerprint (stats, flavor-map) y calentamiento."""

import subprocess
import sys

from app.main import app
from app.services import flavors as flavors_svc
from app.services import stats_service
from app.services.semantic import _build_index, semantic_search
from fastapi.testclient import TestClient

client = TestClient(app)


def test_stats_endpoint_cached_consistent(client):
    r1 = client.get("/stats").json()
    r2 = client.get("/stats").json()
    assert r1 == r2
    assert stats_service._cache_stats is not None
    assert r1["products"] == 2


def test_stats_cache_invalidated_on_fingerprint_change(client, session_factory):
    first = client.get("/stats").json()
    assert first["products"] == 2
    session = session_factory()
    try:
        stats_service._cache_fingerprint = ("otro",)
        stats_service._cache_stats = None
        recomputed = stats_service.compute_stats(session)
        assert recomputed.products == 2
        assert stats_service._cache_stats is recomputed
    finally:
        session.close()
        stats_service.reset_cache()


def test_flavor_map_cached_and_valid(client):
    r1 = client.get("/flavor-map").json()
    r2 = client.get("/flavor-map?detail=true").json()
    assert len(flavors_svc._payload_cache) >= 2
    assert r1["axes"] == r2["axes"]
    assert not r1["detail"] and r2["detail"]
    for cont in r1["continents"]:
        assert set(cont["profile"]) == set(r1["axes"])


def test_warmup_runs_clean(session_factory):
    # Ejecutar el warmup contra la sesión de prueba vía monkeypatch del engine.
    import app.services.warmup as w
    from app.db.database import get_session as real_get_session  # noqa: F401

    original = w.SessionLocal
    try:
        w.SessionLocal = session_factory
        errors = w.run_warmup()
        assert errors == []
        assert w._done.is_set()
    finally:
        w.SessionLocal = original


def test_semantic_index_built_after_warmup(session_factory):
    session = session_factory()
    try:
        _build_index(session)
        hits = semantic_search(session, "kimchi", limit=3)
        assert isinstance(hits, list)
    finally:
        session.close()


def test_warmup_env_gate():
    code = (
        "import os;"
        "os.environ['CONSERVAS_WARMUP']='0';"
        "from app.services.warmup import start_background_warmup;"
        "print(start_background_warmup())"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert out.stdout.strip() == "None"