# Feature Flags

Tabla de flags temporales con fecha de caducidad. Política: eliminar tras promover (ver PLAN_SPRINTS.md regla 8).

| Nombre | Tipo | Default | Razón | Creado | Expira | Owner | Remove_after |
|---|---|---|---|---|---|---|---|
| CONSERVAS_SEARCH_BACKEND/SEARCH_BACKEND | enum(sqlite\|pg\|like) | sqlite | Desacoplar búsqueda FTS5→tsvector (P0-1,P0-4) | 2026-10-03 | 2027-01-01 | backend | Migración PG completa + umbral OK |
| FEATURE_SEARCH_PG_ROLLOUT | bool | false | Dual-read/log-only staging (P0-3) | 2026-10-03 | 2027-01-01 | backend | Tras validar relevancia |
| ENABLE_NC_DATA | bool | false | Aislar datos NC (P0-8) | 2026-10-03 | TBD | legal+backend | Decisión comercial definitiva |
| COMMERCIAL_READY | bool | false | Firewall mezcla comercial (P0-6) | 2026-10-03 | TBD | legal+backend | Si vía comercial activa |
| LOCALSTORAGE_COEXISTENCE_ENABLED | bool | false | Lectura dual local+servidor (P0-9) | 2026-10-03 | 2026-12-01 | frontend+backend | Tras consolidación 9b |
| LOCALSTORAGE_MIGRATION_DRYRUN | bool | true | Forzar dry-run hasta confirm (P0-11) | 2026-10-03 | 2026-12-01 | backend | Tras migración completada |
| FEATURE_PUSH_NOTIFICATIONS | bool | false | Rollout push (N11) | 2026-10-03 | TBD | frontend+backend | Tras estabilizar |

**Reglas:** 
- Flag temporal DEBE tener expires_at. 
- Promovido a permanente → eliminar de esta tabla.
- Logging obligatorio al conmutar (implantar al usar flags).
