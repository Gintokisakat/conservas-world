# 0B — PostgreSQL FTS: tsvector + GIN vs pg_trgm

- **Tema:** FASE 0 - 0B
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Comparar equivalencia entre FTS5 (SQLite) con `bm25(products_fts, ?)` y PostgreSQL (`tsvector` + GIN + `ts_rank`/`ts_rank_cd`) para no romper relevancia.

## 1. Estado actual (SQLite)

`app/api/routes.py` usa FTS5:
- Tabla/índice virtual `products_fts` (columnas relevantes para búsqueda)
- Búsqueda con `MATCH ?` y orden con `bm25(products_fts, ?)` (línea ~101 según análisis)
- Fallback `_fts_matches` → `LIKE` si FTS5 falla

**Riesgo:** cambio de motor altera ranking. Necesitamos conjunto canónico de queries + umbral.

## 2. PostgreSQL: opciones

### Opción A: tsvector + GIN (recomendado para relevancia lingüística)
- `tsvector`: tokeniza, normaliza, elimina stopwords, stem según configuración de idioma
- Índice GIN sobre `tsvector` (rápido para MATCH `@@ to_tsquery`)
- Ranking: `ts_rank(tsv, q)`, `ts_rank_cd(tsv, q)` (considera cercanía, densidad)
- Soporta pesos (`A,B,C,D`), sinónimos, diccionarios, `unaccent` (extensión)

Configuraciones a evaluar:
- `pg_catalog.spanish` + `pg_catalog.english` (multi-idioma) o `simple` (sin stemming, más predecible)
- `unaccent` para quitar acentos
- `to_tsquery` (booleano/lógico) vs `websearch_to_tsquery` (más natural)

### Opción B: pg_trgm (trigramas)
- Basado en similitud (`similarity()`, `%` operador), no lingüístico (stemming/stopwords)
- Útil para fuzzy, errores ortográficos, nombres propios
- Índice GIN/GiST. Ranking por similitud
- Menos preciso para relevancia semántica multi-palabra vs FTS

**Recomendación preliminar:** **A (tsvector+GIN)** para equivalencia con FTS5 + ranking. **B (pg_trgm)** complementario para fuzzy (OR combinado) si hay muchas variantes.

## 3. Equivalencia con bm25

FTS5 `bm25()` penaliza longitud de documento y frecuencia. `ts_rank` usa modelo probabilístico diferente (Cover Density). No son numéricamente idénticos.

**Estrategia:** no buscar igualdad numérica, buscar **equivalencia de orden (ranking)**:
- Métricas: Jaccard top-10, Kendall tau top-k, NDCG@10
- Umbral de aceptación (propuesto): Jaccard@10 ≥ 0.80 y Kendall τ@10 ≥ 0.70 (o acordar tras pruebas). Ajustable en `P0-2`.

## 4. Conjunto de queries canónico (≥20)

Categorías:
1. Nombres exactos (ej. "kimchi", "sauerkraut")
2. Parciales ("ferment")
3. Con acentos ("morcilla", "escabeche")
4. Sin acentos ("morcilla" vs buscar "morcila")
5. Sinónimos/variantes
6. Multi-palabra ("chucrut de col")
7. Compuestos
8. Errores comunes

Crear `tests/data/search_queries.json` (P0-2).

## 5. Implementación técnica

Columnas: `tsv = tsvector('spanish', coalesce(nombre,'')) || tsvector('english', coalesce(nombre,'')) || ...` (ponderar campos). Usar pesos A/B/C.

Índice: `CREATE INDEX CONCURRENTLY idx_products_tsv ON products USING GIN(tsv);`

Consulta ejemplo:
```sql
SELECT id, nombre, ts_rank(tsv, websearch_to_tsquery('spanish', $1)) as rank
FROM products
WHERE tsv @@ websearch_to_tsquery('spanish', $1)
ORDER BY rank DESC, id
```

## 6. DoD 0B

- [ ] Documento comparativo con ejemplos numéricos (mín. 10 queries)
- [ ] Decisión: tsvector+GIN puro vs híbrido (tsvector + pg_trgm)
- [ ] `tests/data/search_queries.json` creado con ≥20 casos + resultados esperados SQLite (top-10)
- [ ] Especificar umbral de aceptación para P0-2
- [ ] ADR breve o añadir a ADR-0001/ADR de migración búsqueda

## Referencias
- Postgres FTS: https://www.postgresql.org/docs/current/textsearch.html
- pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html
- bm25 (FTS5): https://sqlite.org/fts5.html#bm25_function
- docs/PLAN_SPRINTS.md FASE 0 - 0B
- docs/DEVIL_ADVOCATE_TASKS.md P0-2,P0-4
