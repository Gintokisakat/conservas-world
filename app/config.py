import os
from pathlib import Path

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "build.db"
DB_PATH = Path(os.environ.get("CONSERVAS_DB", str(_DEFAULT_DB)))
DB_URL = f"sqlite:///{DB_PATH}"

# Configuración de sitio
SITE_URL = os.environ.get("CONSERVAS_SITE_URL", "https://conservas-del-mundo.onrender.com")

# CORS
CORS_ORIGINS = os.environ.get("CONSERVAS_CORS_ORIGINS", "*")