"""Tests de configuración de despliegue: env CONSERVAS_DB y healthcheck degradado."""

import os
import subprocess
import sys
from pathlib import Path

from app import config
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app, raise_server_exceptions=False)


def test_db_path_default():
    assert config.DB_PATH.name == "build.db"
    assert config.DB_URL.startswith("sqlite:///")


def test_db_path_env_override():
    code = (
        "from app.config import DB_PATH; "
        "print(DB_PATH)"
    )
    env = {**os.environ, "CONSERVAS_DB": "/tmp/opencode/override.db"}
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, check=True
    )
    assert Path(out.stdout.strip()) == Path("/tmp/opencode/override.db")


def test_health_ok_with_real_db():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    # En CI (sin build.db) la BD queda vacía; localmente debe estar ok.
    assert body["db"] in {"ok", "empty"}
    if body["db"] == "empty":
        assert body["status"] == "degraded"


def test_boot_without_db_does_not_crash(tmp_path):
    """La app arranca aunque la BD no exista: health 200 y la home se sirve."""
    code = (
        "from fastapi.testclient import TestClient;"
        "from app.main import app as a;"
        "c = TestClient(a, raise_server_exceptions=False);"
        "print(c.get('/api/health').status_code, c.get('/').status_code)"
    )
    env = {**os.environ, "CONSERVAS_DB": str(tmp_path / "missing.db")}
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, check=True
    )
    assert out.stdout.strip() == "200 200"


def test_deploy_files_exist():
    root = Path(__file__).resolve().parent.parent
    assert (root / "render.yaml").exists()
    assert (root / "Dockerfile").exists()
    assert (root / "docker-entrypoint.sh").exists()
    entry = (root / "docker-entrypoint.sh").read_text()
    assert "ingest.ingest" in entry
    render = (root / "render.yaml").read_text()
    assert "ingest.ingest" in render and "healthCheckPath" in render