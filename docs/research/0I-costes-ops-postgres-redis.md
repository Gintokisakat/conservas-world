# 0I — Costes y operación (Postgres gestionado + Redis)

- **Tema:** FASE 0 - 0I
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Comparativa de proveedores, PITR, límites, coste mensual. Prepara Sprint 3.

## 1. Proveedores a comparar

| Proveedor | Postgres gestionado | PITR | Backups automáticos | Conexiones | Réplicas | Free tier | Notas |
|---|---|---|---|---|---|---|---|
| Render | Sí | Depende plan | Sí | limitado | limitado | limitado | Ya usado (render.yaml) |
| Neon | Sí (serverless) | Sí (branching + PITR según plan) | Sí | auto-scale | disponible | generoso | cold start posible |
| Supabase | Sí | Sí | Sí | pooler | según plan | generoso | incluye auth/otros servicios |

## 2. Requisitos operativos

- **PITR:** obligatorio (recuperar a punto en tiempo tras fallo)
- **Restore ensayado:** Sprint 3 exige ensayo documentado
- **Conexiones:** suficiente con pooler (SQLAlchemy + pool)
- **Backups verificados:** integridad tras restore
- **Múltiples réplicas futuro:** Redis necesario para rate limits/blocklist

## 3. Redis

Necesario para: rate limiting (IP+cuenta), refresh token blocklist/reuse detection (P0-13), sesiones compartidas entre réplicas.

Opciones: Upstash, Redis Cloud, Render Redis.

## 4. Umbral coste aceptable

Definir **umbral máximo** antes de Sprint 3 (ej. mensual razonable). Documentar criterio de cambio si supera.

## 5. Comparativa con datos

Recopilar precios reales (octubre 2026) para plan mínimo viable con PITR.

## 6. DoD 0I

- [ ] Tabla comparativa completa con precios
- [ ] Requisitos PITR + backups verificados
- [ ] Decisión Postgres + umbral coste
- [ ] Decisión Redis (proveedor + coste)
- [ ] Cold start / límites conexiones documentados
- [ ] Prepara Sprint 3, P0-13

## Referencias
- Neon: https://neon.tech/docs/
- Supabase: https://supabase.com/docs
- Render Postgres: https://render.com/docs/databases
- docs/PLAN_SPRINTS.md FASE 0 - 0I, Sprint 3
- docs/DEVIL_ADVOCATE_TASKS.md P0-13,P0-14

## Notas implementación (P0-13)
- Rate limiting compartido entre réplicas → Redis
- Blocklist refresh tokens + reuse detection → Redis (TTL automático)
- Verificar conexión con retry/backpressure
