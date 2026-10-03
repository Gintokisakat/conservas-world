#!/usr/bin/env python
"""Migración localStorage → cuenta (P0-11). Dry-run por defecto."""

import argparse
import json
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path("data/localstorage_backups")
DATA_KEYS = ["pantry_timers", "pantry_prod", "pantry_favs"]


def backup_localstorage(snapshot: dict) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    p = BACKUP_DIR / f"localstorage_{ts}.json"
    p.write_text(json.dumps(snapshot, indent=2))
    return p


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", default=True)
    p.add_argument("--confirm", action="store_true")
    p.add_argument("--input", help="JSON con localStorage")
    args = p.parse_args()

    if args.confirm:
        args.dry_run = False

    snapshot = {}
    if args.input and Path(args.input).exists():
        snapshot = json.loads(Path(args.input).read_text())

    if not args.dry_run:
        b = backup_localstorage(snapshot)
        print(f"BACKUP: {b}")
        print("Migración simulada (consolidar en /me/batches)")
    else:
        print("DRY-RUN: sin cambios")
        for k in DATA_KEYS:
            print(f"  {k}: {len(snapshot.get(k, []))} elementos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
