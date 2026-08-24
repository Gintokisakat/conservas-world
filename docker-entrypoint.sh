#!/bin/sh
set -e

DB_PATH="${CONSERVAS_DB:-/app/data/build.db}"

if [ ! -s "$DB_PATH" ]; then
  echo ">>> build.db no encontrada; generando base de datos (esto puede tardar)..."
  uv run python -m ingest.ingest
fi

exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
