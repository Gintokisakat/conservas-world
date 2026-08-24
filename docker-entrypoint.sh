#!/bin/sh
set -e

DB_PATH="${CONSERVAS_DB:-/app/data/build.db}"

if [ ! -s "$DB_PATH" ]; then
  echo ">>> build.db no encontrada; restaurando snapshot del release..."
  if uv run python -m ingest.restore; then
    echo ">>> BD restaurada."
  else
    echo ">>> Sin snapshot disponible; generando base de datos (puede tardar)..."
    uv run python -m ingest.ingest
  fi
fi

exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
