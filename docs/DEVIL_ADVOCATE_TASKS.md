## 2. Tareas preventivas para evitar esos escenarios

Añadir al roadmap como **FASE 0 — Blindaje preventivo** (inmediatamente antes del Sprint 0 actual) y ajustar los sprints para romper el acoplamiento.

### P0 — Romper el acoplamiento de búsqueda (razón 1)

- **[P0-1] Feature flag de backend de búsqueda** (`SEARCH_BACKEND = sqlite|pg|like`, env). Añadir en `app/config.py` y enrutar en `app/api/routes.py`. Permite conmutar sin redeployar código. (2 h)
- **[P0-2] Suite de regresión de relevancia canónica**: crear `tests/data/search_queries.json` (≥20 queries reales: nombre, sinónimo, acento, parcial). Comparar top-10 entre backends con métrica (Jaccard + Kendall tau) y **umbral de aceptación** en CI. (4 h)
- **[P0-3] Dual-read de búsqueda en staging**: ejecutar ambos backends en paralelo por request (log-only) y guardar diffs. Exigir igualdad dentro del umbral antes de promover a producción. (2 h)
- **[P0-4] Extracción del SQL FTS5 a un adaptador** (`SearchRepo` interfaz): `SqliteFtsRepo`, `PgTsvectorRepo`, `LikeRepo`. Esto desacopla el endpoint del motor (evita tocar 20 sitios a la vez). (5 h)

**Esfuerzo P0 búsqueda:** ~13 h. Mover a **pre-Sprint 1**.

### P0 — Blindaje legal y trazabilidad de datos (razón 2)

- **[P0-5] Inventario de fuentes con metadatos de licencia por fila**: añadir a modelos/ingesta `source`, `source_id`, `source_license` (SPDX o cadena), `source_url`, `commercial_use_allowed` (bool), `derivatives_allowed` (bool), `share_alike` (bool). Exigir estos campos en todas las filas importadas. (6 h)
- **[P0-6] Política de mezcla (license firewall)**: en ingesta, rechazar o marcar `non_commercial_only=true` si una fila NC se intenta mezclar en un dataset con bandera `COMMERCIAL_READY`. Añadir test que falle si se viola. (3 h)
- **[P0-7] Matriz de compatibilidad ODbL**: documentar qué combinaciones son permitidas (mezcla con SA vs propietario). Añadir gate en CI (`scripts/check_license_compat.py`) que inspecciona el build. (3 h)
- **[P0-8] Purga/aislamiento explícito de FermFooDb (NC-ND)**: mantenerlo en un dataset separado, sin indexarlo en la búsqueda comercial, con feature flag `ENABLE_NC_DATA` (default `false`). (2 h)

**Esfuerzo P0 legal:** ~14 h. Debe hacerse **en Sprint 0 y completarse antes de tocar ingestas**.

### P0 — Migración segura de datos locales + operación (razón 3)

- **[P0-9] Periodo de coexistencia lectura dual**: leer lotes/temporizadores de `localStorage` **y** del servidor cuando hay sesión; nunca sobrescribir en silencio. Mostrar origen (`local|server|merged`) en UI. (4 h)
- **[P0-10] Estrategia de merge con resolución de conflictos**: campo `updated_at` cliente/servidor, regla (last-write-wins con bitácora + lista de conflictos) y UI para resolver duplicados antes de consolidar. (5 h)
- **[P0-11] Migración con *dry-run* y *rollback***: script `scripts/migrate_local_to_account.py --dry-run` que detecta duplicados, tamaño, corrupción; exige aprobación explícita (`--confirm`) y genera backup JSON de `localStorage`. (3 h)
- **[P0-12] Pre-check de migración (gate)**: en el flujo de login/primer sync, bloquear la migración si hay >N conflictos sin resolver. Añadir test E2E. (2 h)
- **[P0-13] Redis para rate limits + refresh**: mover rate limiting y lista de refresh tokens revocados a Redis (o store compartido). Hoy en memoria no sobrevive a despliegues/múltiples réplicas. (4 h)
- **[P0-14] Checkpoint de migración de BD**: snapshot + script de rollback probado en staging antes de tocar producción (documentado y ensayado). (2 h)

**Esfuerzo P0 datos/ops:** ~20 h. Sprint 9 debe dividirse: 9a (coexistencia+dry-run) antes de 3 (migración Postgres), 9b (consolidación) después.

### P0 — Gobernanza y visibilidad

- **[P0-15] Definition of Done por migración crítica**: lista verificable (umbral de relevancia superado, restore ensayado, license check verde, dry-run sin pérdidas, feature flags listos). (1 h)
- **[P0-16] Registro de riesgos (risk log)**: añadir `docs/RISK_LOG.md` con probabilidad/impacto/mitigación y fecha de revisión cada sprint. (1 h)

**Total preventivo:** ~49 h (~4–5 sprints de 2 semanas) repartidos **antes y entre** los sprints existentes, no sumados al final.

## 3. Fase 0 — Temas exactos a investigar o aprender antes de ejecutar

Crear **FASE 0 — Aprendizaje y preparación** (investigación, no código). Orden por dependencia (bloqueantes primero).

| Tema | Por qué lo necesito | Qué investigar/aprender (exacto) | Recursos | Criterio de hecho |
|---|---|---|---|---|
| **0A. Licenciamiento de bases de datos (ODbL, CC)** | Bloquea comercial (razón 2) | Diferencia entre obra derivada vs base de datos derivada (ODbL Art. 2/4), CC BY-NC-ND: ¿qué cuenta como «adaptación» al indexar/meter en embeddings? Compatibilidad entre licencias y *share-alike*. | [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), [CC Legal](https://creativecommons.org/licenses/), [Open Knowledge](https://opendefinition.org/) | ADR firmado con matriz de casos (mezcla, indexado, búsqueda, export, API pública). |
| **0B. PostgreSQL FTS: tsvector + GIN vs pg_trgm** | Necesario para N2 sin romper relevancia (razón 1) | Configuraciones de idioma (`pg_catalog.spanish`, `simple`), `ts_rank`/`ts_rank_cd`, pesos, sinónimos, acentos (`unaccent`), equivalencia con `bm25(products_fts)`. Cuándo usar `pg_trgm` para fuzzy. | [Postgres FTS](https://www.postgresql.org/docs/current/textsearch.html), [pg_trgm](https://www.postgresql.org/docs/current/pgtrgm.html) | Documento con 10–15 queries de prueba + ranking esperado vs SQLite. |
| **0C. Feature flags y rollout seguro** | Desacopla migraciones (razón 1 y 3) | Flags por request/env, read-through, logging de conmutación, rollback instantáneo. Cómo evitar *flag explosion*. | [Martin Fowler - Feature Toggles](https://martinfowler.com/articles/feature-toggles.html), [LaunchDarkly patterns](https://launchdarkly.com/blog/feature-flag-best-practices/) | Especificación de flags (P0-1) y política de caducidad (borrar flags tras promover). |
| **0D. Migración de datos con coexistencia (dual-write/dual-read)** | Evita pérdida irreversible (razón 3) | Last-write-wins vs CRDT ligero, `updated_at` con reloj cliente/servidor, resolución de conflictos y *event sourcing* mínimo. | [Data Migration Patterns](https://martinfowler.com/articles/data-migration-patterns.html) | Diagrama de flujo (login → sync → consolidate) y casos borde (2 pestañas, sin conexión). |
| **0E. Seguridad de identidad (tokens)** | Sprint 4 crítico | Refresh token rotation + reuse detection, jti/blocklist, expiraciones, verificación por email con one-time token (no JWT), rate limiting por IP+cuenta. | [OWASP Auth Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), [RFC 6819](https://datatracker.ietf.org/doc/html/rfc6819) | Checklist de amenazas + decisiones (Redis blocklist vs lista en BD). |
| **0F. Moderación operativa y abuso** | Comunidad exige proceso (razón 3) | Cola de reportes, estados, SLA ligero, auditoría inmutable (bitácora), prevención de represalias, filtrado de spam básico. | [Community Guidelines](https://meta.discourse.org/t/moderation-guidelines), [OWASP Content Security](https://owasp.org/www-project-proactive-controls/v3/en/c1-security-requirements) | Política de moderación (ToS anexo) antes de permitir usuarios externos. |
| **0G. PWA: Push API, Service Worker y sincronización offline** | 4.7 incompleto (push/cámara) y N11 | PushSubscription (VAPID keys), payload, background sync/periodic sync, invalidación de caché con `CACHE_NAME` versionado, estrategia cache-first vs stale-while-revalidate. | [MDN Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API), [Workbox](https://developer.chrome.com/docs/workbox/), [PWABuilder](https://www.pwabuilder.com/) | Prototipo mínimo (suscripción + notificación) y decisión de usar Workbox o SW a medida. |
| **0H. Derecho de datos (GDPR/LOPD)** | Export/borrado (Sprint 5) | Derecho de acceso, rectificación, supresión, portabilidad, retención, cascada de borrado (reviews, batches, imágenes). | [GDPR Art. 17/20](https://gdpr-info.eu/art-17-gdpr/), [AEPD](https://www.aepd.es/es) | Matriz de datos por entidad + procedimiento de borrado verificable (tests). |
| **0I. Costes y operación (Postgres gestionado + Redis)** | Sprint 3, evita sorpresas | PITR, backups, límites, conexiones, réplicas, cold start, coste mensual esperado por proveedor (Render/Neon/Supabase). | [Neon Docs](https://neon.tech/docs/), [Supabase](https://supabase.com/docs), [Render Postgres](https://render.com/docs/databases) | Comparativa con umbral de coste aceptable + criterio de cambio. |
| **0J. Testing E2E resistente (Playwright)** | M6/N6 crítico para dev solo | Fixtures con auth, DB seed aislado por test, retries, flakiness, screenshots en fallo, paralelismo vs aislamiento. | [Playwright Best Practices](https://playwright.dev/docs/best-practices) | Guía de escritura de tests E2E (evitar sleeps, usar locators accesibles). |

**Criterio global de Fase 0:** cada tema se cierra con un **ADR de 1 página** + artefacto verificable (documento, matriz, prototipo o checklist). No se pasa a Sprint 0 hasta que 0A–0J estén cerrados con su DoD.