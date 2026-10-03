# 0C — Feature flags y rollout seguro

- **Tema:** FASE 0 - 0C
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Especificar flags necesarios para desacoplar migraciones (búsqueda, NC data, migración local→cuenta) con caducidad obligatoria.

## 1. Principios

- **Rollback instantáneo:** conmutación via env/config sin redeployar código
- **Caducidad obligatoria:** todo flag temporal debe tener `expires_at` y eliminarse tras promover (regla 8 añadida a PLAN_SPRINTS.md)
- **Read-through simple:** lectura por request/env; evitar flag explosion
- **Logging:** registrar cuándo se conmuta y por qué
- **Default conservador:** `false` salvo flag explícitamente promovido

## 2. Flags propuestos

Basados en P0-1, P0-8, análisis abogado del diablo:

| Flag | Tipo | Default | Alcance | Uso | Caducidad |
|---|---|---|---|---|---|
| `SEARCH_BACKEND` (env) | String/enum | `sqlite` | API búsqueda (`/products/search` y rutas relacionadas) | Permite conmutar entre `sqlite\|pg\|like`. (P0-1) | Eliminar tras migración PG completa y umbral relevancia OK |
| `FEATURE_SEARCH_PG_ROLLOUT` | Bool | `false` | Habilita lectura dual/log-only en staging (P0-3) | Compara ambos backends antes de promover | Tras validación exitosa |
| `ENABLE_NC_DATA` | Bool | `false` | Ingesta + indexado + exposición | Aísla datos NC (FermFooDb NC-ND, etc). (P0-8) | Permanente o hasta decidir política comercial definitiva |
| `LOCALSTORAGE_COEXISTENCE_ENABLED` | Bool | `false` | Cliente (`app.js`) + sync servidor | Lectura dual local+servidor. (P0-9) | Eliminar tras consolidación 9b |
| `LOCALSTORAGE_MIGRATION_DRYRUN` | Bool | `true` | Script migración | Fuerza dry-run hasta `--confirm`. (P0-11) | Eliminar tras 9b |
| `COMMERCIAL_READY` | Bool | `false` | Ingesta/license firewall | Impide mezclar datos no comerciales. (P0-6) | Permanente si hay vía comercial |
| `FEATURE_PUSH_NOTIFICATIONS` | Bool | `false` | PWA push | Rollout gradual (N11) | Eliminar tras estabilizar |

**Nota:** `SEARCH_BACKEND` puede ser env var (`CONSERVAS_SEARCH_BACKEND`) para evitar tocar DB.

## 3. Especificación técnica

### Configuración (`app/config.py`)
Añadir:
```python
SEARCH_BACKEND: str = "sqlite"  # sqlite|pg|like
ENABLE_NC_DATA: bool = False
COMMERCIAL_READY: bool = False
FEATURE_PUSH_NOTIFICATIONS: bool = False
```

Leer desde env con validación (pydantic-settings). Valores inválidos → error claro.

### Enrutado búsqueda (`app/api/routes.py`)
Crear `SearchRepo` (P0-4). Selector:
```python
backend = settings.SEARCH_BACKEND
if backend == "pg": repo = PgTsvectorRepo(...)
elif backend == "like": repo = LikeRepo(...)
else: repo = SqliteFtsRepo(...)
```

### Logging de conmutación
Loggear: `search.backend.changed` con `{from,to,reason,actor}`. Útil para auditoría.

### Caducidad obligatoria
Cada flag temporal debe tener entrada en `docs/FLAGS.md` con:
- `name`, `type`, `default`, `reason`, `created_at`, `expires_at`, `owner`, `remove_after`
- Checklist: eliminado tras promover

## 4. Política de caducidad

- Crear `docs/FLAGS.md` (temporal) con inventario
- Al promover flag a permanente → mover a config + eliminar de FLAGS.md
- CI podría fallar si flag con `expires_at < now+30d` sin acción? (opcional)
- Regla 8: «Sin flags temporales sin fecha de caducidad. Todo feature flag debe tener fecha de caducidad y eliminarse tras promover.»

## 5. DoD 0C

- [ ] `app/config.py` actualizado con flags validados
- [ ] `docs/FLAGS.md` creado con tabla + política
- [ ] Especificación de logging de conmutación
- [ ] Validación: env inválido falla con mensaje claro
- [ ] Verificación con `SEARCH_BACKEND` (prepara P0-1)
- [ ] Política de caducidad documentada y aplicable

## Referencias
- Martin Fowler - Feature Toggles: https://martinfowler.com/articles/feature-toggles.html
- LaunchDarkly patterns: https://launchdarkly.com/blog/feature-flag-best-practices/
- docs/PLAN_SPRINTS.md FASE 0 - 0C, regla 8
- docs/DEVIL_ADVOCATE_TASKS.md P0-1,P0-8
- docs/DEVIL_ADVOCATE_ANALYSIS.md Razón 1
