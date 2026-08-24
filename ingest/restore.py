"""Restaura data/build.db desde el artefacto preconstruido de un release.

Evita ejecutar la ingesta completa durante los deploys: las IPs de
datacenter reciben 429/503 de Wikipedia y Open Food Facts, lo que tumba
el build. Si la descarga o la validación fallan, se sale con error para
que el llamador caiga a `python -m ingest.ingest`.

URL configurable con CONSERVAS_DB_RELEASE.
"""

import gzip
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

from httpx import get

DEFAULT_RELEASE_URL = (
    "https://github.com/Gintokisakat/conservas-world/releases/latest/download/build.db.gz"
)
MIN_PRODUCTS = 500


def validate_db(path: Path) -> tuple[bool, str]:
    """Comprueba integridad y contenido mínimo de una BD candidata."""
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            conn.execute("PRAGMA integrity_check")
            (n,) = conn.execute("SELECT count(*) FROM products").fetchone()
        finally:
            conn.close()
    except Exception as exc:
        return False, f"BD inválida: {exc}"
    if n < MIN_PRODUCTS:
        return False, f"BD incompleta: {n} productos (<{MIN_PRODUCTS})"
    return True, f"{n} productos"


def restore(target: Path | None = None, url: str | None = None) -> bool:
    target = target or Path("data/build.db")
    url = url or os.environ.get("CONSERVAS_DB_RELEASE", DEFAULT_RELEASE_URL)

    with tempfile.TemporaryDirectory() as tmp:
        gz_path = Path(tmp) / "build.db.gz"
        try:
            resp = get(url, follow_redirects=True, timeout=120)
            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP {resp.status_code}")
            gz_path.write_bytes(resp.content)
        except Exception as exc:
            print(f"[restore] Descarga fallida ({url}): {exc}")
            return False

        db_path = Path(tmp) / "build.db"
        try:
            with gzip.open(gz_path, "rb") as fin, open(db_path, "wb") as fout:
                shutil.copyfileobj(fin, fout)
        except Exception as exc:
            print(f"[restore] Descompresión fallida: {exc}")
            return False

        ok, detail = validate_db(db_path)
        if not ok:
            print(f"[restore] {detail}")
            return False

        target.parent.mkdir(parents=True, exist_ok=True)
        tmp_target = target.with_suffix(".db.tmp")
        shutil.move(str(db_path), str(tmp_target))
        os.replace(tmp_target, target)
        print(f"[restore] BD instalada en {target} ({detail})")
        return True


def main() -> int:
    if restore():
        return 0
    print("[restore] No se pudo restaurar; usar 'python -m ingest.ingest'")
    return 1


if __name__ == "__main__":
    sys.exit(main())
