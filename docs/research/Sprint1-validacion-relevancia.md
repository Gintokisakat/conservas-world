# Sprint 1: Validación de relevancia (Jaccard/Kendall)

## Objetivo
Verificar que PostgreSQL tsvector+GIN produzca ranking equivalente a SQLite FTS5 (baseline). Umbrales: Jaccard@10 ≥ 0.8, Kendall τ@10 ≥ 0.7.

## Pasos (staging con Postgres)

1. Configurar Postgres con esquema + migración 001_tsvector aplicada
2. Importar dataset idéntico (4.259 productos)
3. Habilitar FEATURE_SEARCH_PG_ROLLOUT=true (dual-read log-only)
4. Ejecutar comparación con queries canónicas:
   - Con flag activo, registrar resultados PG vs SQLite para cada query
   - Usar scripts/compare_search_relevance.py para calcular métricas
5. Si supera umbrales → set SEARCH_BACKEND=pg en staging tras validación
6. Solo entonces promover a producción

## Baseline actual
data/search_baseline_sqlite.json (SQLite FTS5, top10)

## Comandos

```bash
# comparar (cuando PG disponible)
# python scripts/compare_search_relevance.py --pg-url $DATABASE_URL
# revisar data/search_relevance_dual.json
```

## Notas
- Dual-read ya implementado (routes.py) - solo log cuando flag activo
- PgTsvectorRepo implementado con ts_rank + websearch_to_tsquery('simple', ...)
- Índice GIN creado en migración
