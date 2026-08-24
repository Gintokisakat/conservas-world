import os
from pathlib import Path

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "build.db"
DB_PATH = Path(os.environ.get("CONSERVAS_DB", str(_DEFAULT_DB)))
DB_URL = f"sqlite:///{DB_PATH}"