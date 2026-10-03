# 0D — Migración de datos con coexistencia (dual-read/merge)

- **Tema:** FASE 0 - 0D
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Evitar pérdida irreversible de datos en `localStorage` (razón 3). Especificar coexistencia lectura dual, merge con conflictos, dry-run y backup.

## 1. Datos afectados

Identificados en `app/static/app.js`:
- `pantry_timers` — temporizadores (persisten solo en localStorage)
- `pantry_prod` — productos en despensa
- `pantry_favs` — favoritos

Destino servidor: `/me/batches` (`app/api/batches.py`). Migración cubierta por P0-9–P0-12 y Sprint 9a/9b.

## 2. Principios

- **Nunca sobrescribir en silencio** (P0-9)
- **Lectura dual activa durante coexistencia**: leer local + servidor cuando hay sesión, mostrar origen
- **Merge explícito** con resolución de conflictos
- **Dry-run obligatorio** antes de consolidar (P0-11)
- **Backup JSON antes de cualquier escritura** (P0-11)

## 3. Modelo de entidades

Cliente (localStorage):
- IDs locales (UUID/slug) + `updated_at` (ISO 8601)
- Estados, checkpoints, timestamps

Servidor (`batches`):
- ID servidor, `user_id`, `updated_at` (DB), `sync_source` opcional

## 4. Estrategia de merge

**Regla base:** Last-Write-Wins (LWW) con bitácora + lista de conflictos (P0-10).

Definición de conflicto:
- Mismo ítem existe en local y servidor
- Ambos modificados desde última sincronización conocida (`last_sync_at`)
- Diferencia semántica no trivial (no solo metadatos)
- `updated_at` muy cercano o ambigua

Resolución:
1. Comparar `updated_at` (cliente vs servidor). Preferir el más reciente
2. Si diferencia < 60s o campos críticos difieren → marcar como **conflicto** (requiere resolución UI)
3. Registrar en bitácora: `{entity, local_id, server_id, winner, fields, reason}`
4. Nunca auto-resolver conflictos silenciosamente

## 5. Diagrama de flujo (login → sync → consolidate)

1. Usuario inicia sesión
2. Cargar estado local (localStorage)
3. **Coexistencia lectura dual** (P0-9): consultar servidor `/me/batches`. Mostrar origen `local|server|merged` en UI
4. Calcular diffs + detectar conflictos (comparar por identidad + `updated_at`)
5. Si hay conflictos → bloquear consolidación, mostrar UI de resolución (P0-12)
6. **Dry-run** (P0-11): `scripts/migrate_local_to_account.py --dry-run` → genera reporte sin escribir
7. Si OK + sin conflictos sin resolver → consolidar con `--confirm` → backup JSON previo
8. Marcar `last_sync_at`, limpiar/normalizar IDs, desactivar coexistencia tras 9b

## 6. Casos borde

- Multi-pestaña: cambios entre pestañas antes de sync → conflictos esperados
- Sin conexión: seguir leyendo/escribiendo local, sync al reconectar
- Datos corruptos en localStorage (JSON roto) → detectar, reportar, ofrecer importar backup
- IDs locales colisionan → reasignar con mapeo
- Primer login sin datos locales

## 7. Scripts y gates

- `scripts/migrate_local_to_account.py`: `--dry-run`, `--confirm`, genera backup JSON (P0-11)
- Pre-check: bloquear si conflictos sin resolver > 0 (P0-12)
- Gate CI: `migration-dry-run` (sección 4 PLAN_SPRINTS)

## 8. DoD 0D

- [ ] Diagrama de flujo (login→sync→consolidate) documentado
- [ ] Matriz de conflictos con reglas de resolución
- [ ] Especificación lectura dual + origen en UI
- [ ] Especificación dry-run + backup JSON + confirm
- [ ] Casos borde cubiertos
- [ ] Prepara P0-9–P0-12

## Referencias
- Data Migration Patterns (Martin Fowler): https://martinfowler.com/articles/data-migration-patterns.html
- docs/PLAN_SPRINTS.md FASE 0 - 0D, Sprint 9a/9b
- docs/DEVIL_ADVOCATE_TASKS.md P0-9–P0-12
- docs/DEVIL_ADVOCATE_ANALYSIS.md Razón 3
