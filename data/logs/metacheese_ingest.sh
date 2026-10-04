#!/usr/bin/env bash
# Espera a que termine el pipeline de imágenes y luego ejecuta la ingesta de
# metagenomas MetaCheeseDB sobre data/build.db (crea cheese_metagenomes y la
# tabla metagenome que aún falta en la BD real).
set -u

LOG="/home/epil/Proyectos/conservas-world/data/logs/metacheese_ingest.log"
DIR="/home/epil/Proyectos/conservas-world"

echo "[wait] $(date '+%F %T') esperando a que termine el pipeline de imágenes..." >> "$LOG"

while pgrep -f "ingest.images" > /dev/null 2>&1; do
    sleep 60
done

echo "[run] $(date '+%F %T') pipeline de imágenes terminado; ejecutando metacheese..." >> "$LOG"

cd "$DIR"
uv run python -u -m ingest.ingest --sources metacheese >> "$LOG" 2>&1

echo "[done] $(date '+%F %T') ingesta metacheese finalizada (exit $?)" >> "$LOG"

# Verificación: nº de filas en cheese_metagenomes
uv run python -u -c "
from app.db.database import SessionLocal
from sqlalchemy import text
s = SessionLocal()
try:
    n = s.execute(text('select count(*) from cheese_metagenomes')).scalar()
    print(f'cheese_metagenomes: {n} filas')
except Exception as e:
    print('ERROR verificando:', e)
finally:
    s.close()
" >> "$LOG" 2>&1