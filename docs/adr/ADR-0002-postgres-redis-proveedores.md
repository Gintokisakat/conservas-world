# ADR-0002: Proveedores Postgres gestionado + Redis

- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Autor:** Decisión técnica (Sprint 3)
- **Relacionado:** docs/PLAN_SPRINTS.md Sprint 3, docs/research/0I-costes-ops-postgres-redis.md

## Contexto

Necesitamos Postgres gestionado con PITR, backups, pooler. Redis para rate limits + refresh blocklist (P0-13). Comparativa hecha en 0I.

## Criterios
- PITR disponible
- Backups automáticos + verificados
- Pooler/conexiones suficientes
- Coste razonable
- Facilidad staging/local
- Cold start aceptable

## Comparativa rápida (octubre 2026 orientativo)

| Proveedor | PITR | Free tier usable? | Estimado mínimo | Notas |
|---|---|---|---|---|
| Render | Parcial según plan | Limitado | ~7–15$/mes | Ya en render.yaml; PITR puede requerir plan superior |
| Neon | Sí (según plan) | Generoso para dev/staging | ~0–10$/mes | Serverless, branching útil |
| Supabase | Sí | Generoso | ~0–10$/mes | Todo-en-uno, pooler incluido |

## Decisión preliminar

**Postgres:** Neon (desarrollo + staging ágiles, branching, PITR según plan). **Alternativa:** Supabase si queremos menos fricción.

**Redis:** Upstash (serverless, TTL, fácil, razonable). Alternativa Render Redis.

## Umbral coste aceptable

Máximo razonable: ~15–20$/mes total (PG+Redis) para MVP comunitario inicial. Revisar si supera.

## Acción
- Crear variables: DATABASE_URL (Postgres), REDIS_URL
- Usar SSL, pool_pre_ping, pool_recycle
- Ensayar restore/PITR en staging (Sprint 3)
- Migrar schema con Alembic (001_tsvector ya existe)

## Estado
**Draft** — elegir proveedor concreto y confirmar PITR antes de producción
