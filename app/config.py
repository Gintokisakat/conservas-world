import os
from pathlib import Path

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "build.db"
DB_PATH = Path(os.environ.get("CONSERVAS_DB", str(_DEFAULT_DB)))
DB_URL = f"sqlite:///{DB_PATH}"

# Configuración de sitio
SITE_URL = os.environ.get("CONSERVAS_SITE_URL", "https://conservas-del-mundo.onrender.com")

# CORS
CORS_ORIGINS = os.environ.get("CONSERVAS_CORS_ORIGINS", "*")

# Feature flags (FASE 0C / P0-1)
# SEARCH_BACKEND: sqlite|pg|like
SEARCH_BACKEND = os.environ.get("CONSERVAS_SEARCH_BACKEND", "sqlite").strip().lower()
if SEARCH_BACKEND not in ("sqlite", "pg", "like"):
    SEARCH_BACKEND = "sqlite"

ENABLE_NC_DATA = os.environ.get("CONSERVAS_ENABLE_NC_DATA", "false").lower() == "true"
COMMERCIAL_READY = os.environ.get("CONSERVAS_COMMERCIAL_READY", "false").lower() == "true"
FEATURE_PUSH_NOTIFICATIONS = os.environ.get("CONSERVAS_FEATURE_PUSH_NOTIFICATIONS", "false").lower() == "true"
FEATURE_SEARCH_PG_ROLLOUT = os.environ.get("CONSERVAS_FEATURE_SEARCH_PG_ROLLOUT", "false").lower() == "true"
LOCALSTORAGE_COEXISTENCE_ENABLED = os.environ.get("CONSERVAS_LOCALSTORAGE_COEXISTENCE_ENABLED", "false").lower() == "true"
LOCALSTORAGE_MIGRATION_DRYRUN = os.environ.get("CONSERVAS_LOCALSTORAGE_MIGRATION_DRYRUN", "true").lower() == "true"
