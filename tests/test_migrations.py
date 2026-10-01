"""Tests de migraciones Alembic (roadmap 5.1)."""
import importlib
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture()
def db_loader(monkeypatch):
    """Carga app.db.database contra una BD temporal y restaura todo al final.

    Cambiar CONSERVAS_DB y recargar el módulo crea un engine nuevo; si eso se
    filtra, los tests siguientes usarían la base equivocada. Se guardan el
    entorno y sys.modules para dejar el proceso como estaba.
    """
    saved_modules = {
        name: mod
        for name, mod in sys.modules.items()
        if name == "app.config" or name.startswith("app.db")
    }

    def _invalidate():
        for name in [
            n
            for n in sys.modules
            if n == "app.config" or n.startswith("app.db")
        ]:
            del sys.modules[name]

    def load(db_path):
        # Relargar en cada llamada: la segunda BD necesita su propio engine,
        # no el que quedó cacheado de la primera.
        _invalidate()
        monkeypatch.setenv("CONSERVAS_DB", str(db_path))
        return importlib.import_module("app.db.database")

    yield load

    current = {
        name: mod
        for name, mod in sys.modules.items()
        if name == "app.config" or name.startswith("app.db")
    }
    for mod in current.values():
        engine = getattr(mod, "engine", None)
        if engine is not None:
            engine.dispose()
    for name in current:
        if name not in saved_modules:
            del sys.modules[name]
    sys.modules.update(saved_modules)


@pytest.fixture()
def fresh_db(tmp_path, db_loader):
    """Módulo app.db.database con una BD vacía y migrada por Alembic."""
    mod = db_loader(tmp_path / "fresh.db")
    mod.init_db()
    yield mod


def _tables(path):
    conn = sqlite3.connect(path)
    return {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
    }


def _version(path):
    conn = sqlite3.connect(path)
    return [r[0] for r in conn.execute("SELECT version_num FROM alembic_version")]


def test_alembic_files_exist():
    assert (ROOT / "alembic.ini").is_file()
    assert (ROOT / "alembic" / "env.py").is_file()
    versions = list((ROOT / "alembic" / "versions").glob("*.py"))
    assert versions, "debe existir al menos la migración baseline"


def test_init_db_creates_schema_via_alembic(fresh_db, tmp_path):
    tables = _tables(tmp_path / "fresh.db")
    assert "products" in tables
    assert "users" in tables
    assert "api_keys" in tables
    assert _version(tmp_path / "fresh.db")


def test_migration_stamps_version(fresh_db, tmp_path):
    version = _version(tmp_path / "fresh.db")
    assert len(version) == 1
    assert version[0]  # hash de revisión


def test_init_db_is_idempotent(fresh_db, tmp_path):
    before = _tables(tmp_path / "fresh.db")
    version_before = _version(tmp_path / "fresh.db")
    fresh_db.init_db()
    fresh_db.init_db()
    assert _tables(tmp_path / "fresh.db") == before
    assert _version(tmp_path / "fresh.db") == version_before


def test_alembic_schema_matches_models(fresh_db, tmp_path, db_loader):
    """La migración baseline debe reproducir exactamente create_all."""
    alembic_tables = _tables(tmp_path / "fresh.db") - {"alembic_version"}

    # Segunda BD creada con el camino create_all (sin Alembic)
    legacy_path = tmp_path / "legacy.db"
    legacy = db_loader(legacy_path)
    legacy.init_db(use_alembic=False)
    create_all_tables = _tables(legacy_path) - {"alembic_version"}

    assert alembic_tables == create_all_tables


def test_preexisting_database_is_stamped_not_recreated(tmp_path, db_loader):
    """Una BD creada antes de Alembic se sella en head y conserva los datos."""
    db_path = tmp_path / "preexisting.db"

    # Simular la base histórica: create_all sin Alembic
    legacy = db_loader(db_path)
    legacy.init_db(use_alembic=False)
    from sqlalchemy import text

    with legacy.engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO users (email, username, password_hash) "
                "VALUES ('a@b.com', 'legacy', 'x')"
            )
        )
    legacy.engine.dispose()
    assert "alembic_version" not in _tables(db_path)

    # Ahora adoptamos Alembic: debe sellar, no re-crear
    mod = db_loader(db_path)
    mod.init_db()

    assert _version(db_path), "debe quedar versionada"
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
    conn.close()
    mod.engine.dispose()


def test_init_db_falls_back_when_alembic_missing(tmp_path, db_loader, monkeypatch):
    """Si Alembic falla, init_db degrada a create_all en vez de romper."""
    mod = db_loader(tmp_path / "fallback.db")

    def boom():
        raise RuntimeError("alembic no disponible")

    monkeypatch.setattr(mod, "_run_alembic_upgrade", boom)
    mod.init_db()

    tables = _tables(tmp_path / "fallback.db")
    assert "products" in tables
    mod.engine.dispose()


def test_env_py_uses_app_config_url():
    env = (ROOT / "alembic" / "env.py").read_text(encoding="utf-8")
    assert "from app.config import DB_URL" in env
    assert "target_metadata = Base.metadata" in env
    # SQLite necesita batch mode para simular ALTER COLUMN
    assert "render_as_batch=True" in env


def test_entrypoint_runs_migrations():
    entry = (ROOT / "docker-entrypoint.sh").read_text(encoding="utf-8")
    assert "alembic upgrade head" in entry
    # La migración debe correr antes de levantar uvicorn
    assert entry.index("alembic upgrade head") < entry.index("uvicorn")


def test_alembic_declared_in_dependencies():
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "alembic" in content
