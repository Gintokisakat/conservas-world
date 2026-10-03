# MoSCoW, cuellos de botella y sprints

Plan de ejecución derivado de la auditoría de lanzamiento.

- **Objetivo a futuro**: convertir el proyecto en algo **comunitario y comercial**, con una
  app (PWA primero) como vehículo. Ver la sección 4 para el punto de bifurcación.
- **Parámetros**: 5-6 h/semana, trabajo en solitario.
- **Fecha**: 2026-10-03.
- **Complementa** a `ROADMAP.md` (qué construir) y `docs/PLAN_LANZAMIENTO.md` (qué impide lanzarlo).

> **Cambio de rumbo (2026-10-03).** La primera versión de este documento asumía un MVP de
> herramienta personal de fermentación. Con el objetivo nuevo —comunidad y comercial— la
> clasificación se invierte: los datos de usuario, la identidad y la persistencia dejan de ser
> «el producto» y pasan a ser la **infraestructura** sobre la que una comunidad puede existir.
> Lo que era *Won't* por ausencia de usuarios ahora es *Must* porque habrá usuarios.

---

## 0. Punto de partida: dos cosas que el roadmap se equivocaba

El roadmap tiene **26 de 31 ítems completados**. Para el objetivo nuevo eso es mejor noticia de
lo que parece, y hay dos correcciones que cambian el plan:

**Lo que el roadmap da por pendiente y ya existe:**

| Ítem | Estado real |
|---|---|
| 4.9 SEO y structured data | **Hecho**: `app/api/seo.py` genera `sitemap.xml`, `robots.txt`, SSR del detalle en `/p/{product_id}` y JSON-LD. Para comunidad, el SEO ya está pagado |
| 4.7 PWA (la parte web) | **Hecho**: `sw.js`, `manifest.json`, icons, botón de instalación. Falta lo que hace que sea una *app*: push y cámara |
| 4.10 Accesibilidad | **Hecho** desde `0bd4091` |

**Lo que falta y el roadmap no emphasises lo bastante:**

| Brecha | Estado real | Por qué importa para comunidad |
|---|---|---|
| Identidad | No hay verificación de email ni reset de contraseña. Solo JWT + refresh | Una cuenta que no se puede recuperar es una cuenta perdida |
| Moderación | Solo el booleano `flagged` y `POST /reviews/{id}/flag` | No hay cola, ni estados de resolución, ni rol admin, ni bitácora |
| Derechos de datos | No hay export ni borrado de cuenta | Obligación legal en UE desde el primer usuario real |

**La conclusión:** el trabajo restante no es construir features, es **convertir un catálogo
monolítico en una plataforma con identidad, datos y reglas**. Y con 5,6 h/semana ≈ 285 h/año,
la comunidad es un programa de años, no de meses. Este plan cubre la fundación (≈7 meses) y
luego se bifurca.


---

## FASE 0 — Aprendizaje y preparación (antes de Sprint 0)

**Regla de oro:** No se escribe código para migraciones críticas hasta cerrar esta fase. Cada tema exige un **ADR de 1 página** + artefacto verificable.

**Duración estimada:** 5–6 h/semana durante 3–4 semanas (~15–20 h).

| # | Tema | Por qué es bloqueante | Qué investigar/aprender | Recursos | Criterio de hecho |
|---|---|---|---|---|---|
| **0A** | **Licenciamiento de bases de datos (ODbL, CC)** | Bloquea vía comercial (razón 2 del abogado del diablo) | Diferencia entre obra derivada vs base de datos derivada (ODbL Art. 2/4), CC BY-NC-ND: ¿qué cuenta como «adaptación» al indexar/meter en embeddings? Compatibilidad entre licencias y *share-alike*. | [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), [CC Legal](https://creativecommons.org/licenses/), [Open Knowledge](https://opendefinition.org/) | ADR firmado con matriz de casos (mezcla, indexado, búsqueda, export, API pública) |
| **0B** | **PostgreSQL FTS: tsvector + GIN vs pg_trgm** | Necesario para migrar sin romper relevancia (razón 1) | Configuraciones de idioma (`pg_catalog.spanish`, `simple`), `ts_rank`/`ts_rank_cd`, pesos, sinónimos, acentos (`unaccent`), equivalencia con `bm25(products_fts)`. Cuándo usar `pg_trgm` para fuzzy. | [Postgres FTS](https://www.postgresql.org/docs/current/textsearch.html), [pg_trgm](https://www.postgresql.org/docs/current/pgtrgm.html) | Documento con 10–15 queries de prueba + ranking esperado vs SQLite |
| **0C** | **Feature flags y rollout seguro** | Desacopla migraciones críticas | Flags por request/env, read-through, logging, rollback instantáneo. Evitar *flag explosion* y caducidad obligatoria. | [Martin Fowler - Feature Toggles](https://martinfowler.com/articles/feature-toggles.html) | Especificación de flags + política de caducidad (eliminar tras promover) |
| **0D** | **Migración de datos con coexistencia (dual-read/merge)** | Evita pérdida irreversible de `localStorage` (razón 3) | Last-write-wins vs CRDT ligero, `updated_at` cliente/servidor, resolución de conflictos, casos borde multi-pestaña/sin conexión. | [Data Migration Patterns](https://martinfowler.com/articles/data-migration-patterns.html) | Diagrama de flujo (login→sync→consolidate) + matriz de conflictos |
| **0E** | **Seguridad de identidad (tokens)** | Crítico para Sprint 4 | Refresh token rotation + reuse detection, jti/blocklist, verificación por email con one-time token (no JWT), rate limiting por IP+cuenta. | [OWASP Auth Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), [RFC 6819](https://datatracker.ietf.org/doc/html/rfc6819) | Checklist de amenazas + decisión Redis blocklist vs BD |
| **0F** | **Moderación operativa y abuso** | Requisito para primer usuario externo | Cola de reportes, estados, auditoría inmutable, SLA ligero, prevención de represalias, spam básico. | [Discourse Moderation Guidelines](https://meta.discourse.org/t/moderation-guidelines) | Política de moderación (anexo a ToS) |
| **0G** | **PWA: Push API, SW y sincronización offline** | Completa 4.7 (push/cámara) y N11 | VAPID, payload, background sync/periodic sync, invalidación con `CACHE_NAME` versionado, cache-first vs stale-while-revalidate. | [MDN Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API), [Workbox](https://developer.chrome.com/docs/workbox/) | Prototipo mínimo (suscripción + notificación) + decisión Workbox vs SW propio |
| **0H** | **Derecho de datos (GDPR/LOPD)** | Export/borrado (Sprint 5) | Acceso, rectificación, supresión, portabilidad, retención, cascada de borrado (reviews, batches, imágenes). | [GDPR Art. 17/20](https://gdpr-info.eu/art-17-gdpr/), [AEPD](https://www.aepd.es/es) | Matriz de datos por entidad + procedimiento de borrado verificable |
| **0I** | **Costes y operación (Postgres gestionado + Redis)** | Evita sorpresas en Sprint 3 | PITR, backups, límites, conexiones, réplicas, cold start, coste mensual (Render/Neon/Supabase). | [Neon Docs](https://neon.tech/docs/), [Supabase](https://supabase.com/docs/), [Render Postgres](https://render.com/docs/databases) | Comparativa con umbral aceptable + criterio de cambio |
| **0J** | **Testing E2E resistente (Playwright)** | Crítico para dev solo (M6/N6) | Fixtures con auth, DB seed aislado, retries, flakiness, screenshots, aislamiento vs paralelismo. | [Playwright Best Practices](https://playwright.dev/docs/best-practices) | Guía E2E (evitar sleeps, usar locators accesibles) |

**DoD FASE 0:** Todos 0A–0J cerrados con ADR + artefacto. No pasar a Fase 0b.
---

## 1. Matriz MoSCoW

### Must have — Sin esto no hay comunidad ni negocio

Ordenados por dependencia, no por dificultad. N1 y N2 van primero porqueeverything lo demás
se construye encima, y porque retrospectivamente son los caros.

| # | Ítem | Por qué es imprescindible | Esfuerzo |
|---|---|---|---|
| N1 | **Decisión de licencias y aislamiento de fuentes NC** | Comercial excluye las licencias **CC BY-NC-***: FooDI-ML (NC-SA), Flavor Network (NC-SA) y FermFooDb (NC-ND) no pueden usarse en un producto comercial. Open Food Facts es **ODbL**, con *share-alike* sobre la base de datos. Decidir esto después significa migrar datos y rehacer la atribución | 6-8 h |
| N2 | **PostgreSQL y reescritura de la búsqueda** | Una comunidad son varios usuarios escribiendo a la vez. SQLite tiene un solo escritor y no hay PITR. La búsqueda es SQL crudo de FTS5 (`products_fts MATCH`, `bm25()`): hay que pasarla a `tsvector` + índice GIN, o `pg_trgm` | 20-40 h |
| N3 | **Identidad real**: verificación de email, reset de contraseña, revocación de sesión | Hoy no hay ninguna de las tres. Sin verificación, el spam es gratis; sin reset, cada usuario perdido es una queja | 8-10 h |
| N4 | **Moderación operativa**: cola de reportes, estados de resolución, rol admin, bitácora | Es el coste de permitir que terceros escriban. Sin moderación, un solo acoso basta para perder el proyecto | 10-12 h |
| N5 | **ToS, privacidad y política de contenido** | Obligatorio antes de que un tercero publique algo. Incluye cómo se moderan reseñas y recetas | 4-5 h |
| N6 | **Playwright (2 flujos)** | Con comunidad, un selector roto deja de ser un annoyance y es una pérdida de usuario. Sigue siendo la única red de un dev solo | 6-8 h |
| N7 | **Invalidación del SW automatizada** | Una app instalada es un cliente que no actualiza si nadie bumpea la caché. Con comunidad, cada fix sin deploy es días de usuarios en versión vieja | 2-3 h |
| N8 | **CORS, rate limits en auth y cabeceras** | `allow_origins="*"` con `allow_credentials=True` en producción, y un rate limit en memoria que un deploy borra | 5-6 h |
| N9 | **Postgres gestionado, PITR y restore ensayado** | El backup de una comunidad no probada no es un backup | 6-8 h |
| N10 | **Lotes y despensa fuera de `localStorage`, en la cuenta** | Con N3 existe una identidad real, así que el dato puede vivir en el servidor. Es lo que convierte la web en una herramienta de uso diario | 6-8 h |
| N11 | **Push notifications** | Es el 80% de una app sin escribir una línea de Kotlin o Swift. Notificación de fermentación lista es la razón de volver cada semana | 5-7 h |

**Total Must: ~90-115 h ≈ 9-11 sprints de 2 semanas.**

### Should have — Con comunidad o con ingresos

| # | Ítem | Esfuerzo | Nota |
|---|---|---|---|
| S1 | Billing y entitlements (Stripe) | 10-14 h | Solo si la vía es comercial de pago directo. Sin esto, «comercial» significa vender datos o API |
| S2 | Cuotas de API por plan | 5 h | Hoy los API keys no tienen límites diferenciados; sin monetize |
| S3 | Imágenes de usuario y cámara | 6-8 h | Fotos de fermentación es el contenido que genera comunidad. Requiere moderación de imágenes |
| S4 | Perfiles públicos y «mis lotes visibles» | 5 h | El mecanismo más barato de comunidad: el usuario muestra su fermentación |
| S5 | Reportes de producto y uso por feature | 6 h | Para decidir comunidad vs comercial con datos, no con opinión |
| S6 | axe-core en CI | 3 h | La dependencia está en el roadmap desde hace meses y nunca se añadió |
| S7 | Alertas de antigüedad del snapshot y de fallo de ingesta | 3 h | Sin esto nadie detecta que producción sirve datos viejos |
| S8 | Dividir `app.js` por dominio | 8 h | 188 KB monolíticos; precondición para editar con seguridad |
| S9 | Onboarding y empty states | 5 h | «Tu primer fermento» y qué hacer sin datos |
| S10 | i18n adicional (fr, pt primero) | 6 h | Solo los idiomas del público que llega. 10 idiomas no son 5,6 h/semana |
| S11 | Runbook, CHANGELOG y notas de release | 5 h | Un proyecto sin dueño del changelog se pudre |
| S12 | Export y borrado de cuenta (GDPR/LOPD) | 4 h | Legal, y encaja con el Sprint de identidad |
| S13 | PWA offline de lotes y cola de sincronización | 8 h | Diferencial de una app real frente a un sitio |

### Could have — Cuando la fundación esté firme

| # | Ítem | Por qué no ahora |
|---|---|---|
| C1 | Moderación asistida por ML | 4-12 h de Sentinel, pero solo tiene sentido con volumen alto |
| C2 | Ingesta programada (cron/worker) en vez de manual | Se repite en cada deploy; viene con N2 |
| C3 | Regresión visual completa | Espera a que Playwright esté en marcha |
| C4 | Export PDF de recetas | CSV cubre el caso real |
| C5 | Microbioma profundo (2.2) | Parsing académico, poco retorno |
| C6 | Integración Fermentor.org (3.7) | Verificar licencia primero |
| C7 | Regresión de i18n por idioma | Cuando S10 añada idiomas |

### Won't have — Explícitamente fuera de este ciclo

| # | Ítem | Motivo |
|---|---|---|
| W1 | **App nativa (React Native)** | La PWA cubre push, cámara, offline e instalación. Nativa es un segundo producto: otro lenguaje, otro store, otro ciclo de release. Solo con una limitación real que la PWA no resuelva |
| W2 | **2.4 Péptidos bioactivos** | CC BY-NC-ND: emparejar una fila por nombre *es* un derivado, y además es NC |
| W3 | **2.5 FoodOn** | Interoperabilidad sin usuario que la pida |
| W4 | **2.8 Open Wine Map** | Solo Europa; el mapa actual cumple |
| W5 | **Marketplace con pagos entre productores** | Cobrar entre terceros significa fiscalidad, reembolsos, disputas y verificación de identidad. Es un negocio entero |
| W6 | **i18n a 10 idiomas** | Cada idioma son ~500 strings, tests y revisión. Con S10 basta |
| W7 | **Multi-tenant u organizaciones** | Nadie lo ha pedido |
| W8 | **Postgres sharding o réplicas** | Optimización prematura; una instancia gestionada aguanta mucho más |
| W9 | **Rediseño visual** | El diseño actual funciona; el cuello es de plataforma, no de píxeles |

### Done — Congelado

Solo tests de regresión. No se aceptan features nuevas sobre estas piezas:

`1.1` nutrición USDA · `1.2` ruff+mypy+CI · `1.3` dark mode · `1.4` autocomplete · `1.5` estacional ·
`1.6` export productos · `1.7` etiquetas de dieta · `1.8` glosario · `2.1` mapa · `2.3` pH/seguridad ·
`2.6` Ark of Taste · `2.7` cervecerías · `2.9` etimología · `2.10` cronología · `2.11` imágenes ·
`2.13` lácteos FDF-DB · `2.14` África/Oriente Medio · `2.15` shelf-life · `2.16` LanguaL ·
`3.2` calculadoras · `3.3` pairings · `3.5` búsqueda semántica · `3.6` mapa de sabores ·
`3.8` temporizadores por temperatura · `3.9` API pública · `3.10` MCP · `4.1` auth base ·
`4.9` SEO · `4.10` a11y

> Notas de precisión: `3.5` usa **TF-IDF propio**, sin sentence-transformers ni FAISS; el roadmap
> lo estimaba en ~80 MB de modelo. `4.9` está implementado y el roadmap no lo marca. `4.7` está a
> medias: la parte web existe, push y cámara no.

---

## 2. Cuellos de botella

Reordenados para el objetivo nuevo. B1 y B2 han cambiado de identidad: antes eran decisiones
económicas, ahora son **decisiones de arquitectura y de legality** que condicionan todo.

| # | Cuello | Prob. | Impacto | Esfuerzo si falla |
|---|---|---|---|---|
| B1 | **PostgreSQL + reescritura de FTS5 (N2)** | Alta | Muy alto | 20-40 h, y toda búsqueda con `bm25()` deja de funcionar |
| B2 | **Licencias y datos NC (N1)** | Baja (técnica) | Muy alto | Bloquea la vía comercial entero; barato ahora, caro en 6 meses |
| B3 | **Identidad + moderación (N3+N4)** | Alta | Muy alto | ~20 h y bloquea N10; además, sin esto no se puede invitar al primer usuario externo |
| B4 | **Ancho de banda de 5,6 h/semana** | Certísima | Alto | El riesgo sistémico. Comunidad significa además soporte y moderación continua, que es trabajo invisible |
| B5 | **El segundo usuario** | Alta | Alto | El propio uso esconde bugs. Sin un usuario externo nunca aparecen los fallos de permisos, de datos ajenos y de abuso |
| B6 | **Comunidad *o* comercial: hay que elegir el orden** | Media | Alto | Cada vía tiene Musts distintos; empezar por la equivocada cuesta un trimestre |
| B7 | **FTS5 atado a SQLite** | Media | Medio | Si se elige disco en vez de Postgres, reaparece en 6 meses con usuarios reales. Decidirlo antes (N2) es lo que lo evita |

### B1 en detalle: por qué ahora sí Postgres

Con un usuario, SQLite con disco persistente bastaba y costaba 2-4 h. Con comunidad cambia
el cálculo en tres cosas:

1. **Escritores concurrentes.** SQLite serializa las escrituras. Un reporte de reseña, un
   lote nuevo y una ingesta concurrentes se serializan o fallan.
2. **Copias de seguridad.** Con PITR de Postgres se recupera a un punto en el tiempo. Con
   SQLite + un `.db` copiado a mano, la ventana de pérdida es del intervalo entre copias.
3. **La búsqueda es SQL crudo.** `products_fts MATCH` y `bm25()` no existen en Postgres. El
   precio de entrada es reescribir la búsqueda con `tsvector` + GIN (o `pg_trgm` para
   difusos), reindexar y revalidar la relevancia a mano.

Mitigación importante: el código ya tiene un *fallback* (`_fts_matches` devuelve `None` si
FTS5 falla y degrada a `LIKE`). Durante la migración, la búsqueda puede quedar en modo
degradado sin romperse. Eso permite migrar sin una ventana de caída.

### B2 en detalle: la decisión más barata y más cara del plan

Si el objetivo es comercial, hay tres fuentes que **no pueden entrar**:

| Fuente | Licencia | Por qué bloquea |
|---|---|---|
| FooDI-ML | CC BY-NC-SA | No comercial + share-alike |
| Flavor Network | CC BY-NC-SA | No comercial + share-alike |
| FermFooDb | CC BY-NC-ND | No comercial + **No Derivatives**: emparejar filas es una obra derivada |

Y una que condiciona el modelo de negocio: **Open Food Facts es ODbL**, con *share-alike* sobre
la base de datos. Si la base es pública, hay que publicarla bajo ODbL o compatible. Si es
privada, ODbL sigue exigiendo acceso gratuito a las bases derivadas, lo que limita un
producto propietario.

La salida no es descartar los datos: es **separar la procedencia por campo**. Hechos curados
propios (por ejemplo, un pairing que has decidido) no heredan la licencia del origen; el texto
verbatim sí. Eso es una decisión de arquitectura de datos con peso legal, y por eso es N1 y no
«un documento que escribir».

### B3 en detalle: identidad y moderación son la factura de la comunidad

Son ~20 h y no producen nada visible: ningún botón, ninguna pantalla. Es exactamente el tipo
de trabajo que se aplaza y que luego bloquea la invitations. Y son la condición para invitar
al primer usuario externo sin convertirte en un refugio de spam.

**Regla dura: no se acepta el primer usuario externo hasta que N3, N4 y N5 estén cerrados.**
Un solo usuario real descubre en minutos los fallos que 600 tests no ven: permisos mal
aislados, datos de otro usuario, contenido que nadie moderaría.

### B4 en detalle: comunidad es un trabajo invisible

Con 5,6 h/semana, el coste no es el trabajo: es **volver al contexto**. Un sprint de 11 h
queda dividido en tres sesiones de menos de 4 h cada una.

Reglas que lo atacan:

1. **Una sesión, un tema.** Tres sesiones, tres temas. Nunca «un poco de todo».
2. **Nota de siguiente acción al cerrar cada sesión.** Una línea: «Siguiente: N2 paso 3,
   índice GIN sobre `tsvector`». Sin esto, la sesión siguiente pierde 20 min releyendo.
3. **Todo fix entra con su test en el mismo commit.** Sin equipo, el test es la única red.
4. **Nada nuevo empieza sin cerrar un Must anterior.** Si un sprint se atasca, se recorta
   alcance; no se alarga el sprint.
5. **Trabajo largo en paralelo de verdad**: lanzar la suite de Playwright o una ingesta y
   mientras escribir documentación, ToS o tests. Es el único paralelismo real sin equipo.
6. **El trabajo de comunidad (moderación, soporte) se agenda, no se improvisa.** Si no tiene
   hueco en el sprint, no se hace: se responde la próxima semana. Sin eso, la comunidad se
   come el roadmap.

### B6 en detalle: comunidad, comercial y app no se construyen en el mismo orden

La fundación (N1-N11) es común a las tres. Lo que sigue diverge:

| Si el objetivo es… | Lo que entra Must después | Lo que se aplaza |
|---|---|---|
| **Comunidad** | Perfiles públicos, lotes visibles, follows, moderación de imágenes, flujo de invitación | Billing, cuotas de API |
| **Comercial** | Billing y entitlements, cuotas por plan, ToS de uso comercial, factura y fiscalidad, soporte | Perfiles y follows |
| **App** | Push, cámara, offline con cola de sync, y **decidir nativa vs PWA con evidencia** | Todo lo demás |

La pregunta que hay que responder antes del Sprint 1 es cuál de las tres va **primero**, porque
las tres compiten por las mismas 5,6 h.

### Cómo paralelizar en solitario

No hay paralelismo por personas, así que el paralelismo es **temporal y de contexto**:

| Situación | Técnica |
|---|---|
| Tarea bloqueante y larga (migración, suite E2E, ingesta) | Lanzarla en segundo plano y avanzar en ToS, docs o tests |
| Dos tareas independientes y pequeñas | Una por sesión, nunca mezcladas |
| Cambios que se tocan entre sí (`app.js`) | Una sola sesión; partir el archivo antes (S8) |
| Trabajo administrativo (licencias, atribución, release notes) | Una sesión quincenal agrupada, no gotas repartidas |
| Moderación y soporte | Ventana fija en el calendario, no «cuando sobre» |

---

## 3. Plan por sprints

**Formato**: sprints de 2 semanas, ~11 h por sprint (5,6 h/semana).
**Total**: 14 sprints ≈ 154 h ≈ **7 meses** hasta tener una fundación sobre la que una
comunidad o un negocio pueden existir. La monetización o la comunidad real empiezan después
del Sprint 14, en la bifurcación de la sección 4.

Ningún sprint empieza con un Must sin cerrar.


---

## FASE 0b — Blindaje preventivo (Pre-Sprints P0)

**Objetivo:** romper el triple acoplamiento (búsqueda + licencias + datos locales) antes de migraciones. Basado en el análisis del abogado del diablo.

**Esfuerzo estimado:** ~49 h (dividido en 2 pre-sprints de 11+11 h + holgura para integración).

### Pre-Sprint P0-1 (11 h) — Búsqueda + Licencias (P0-1–P0-8)

| Tarea | Horas | Notas |
|---|---|---|
| **[P0-1]** Feature flag `SEARCH_BACKEND = sqlite\|pg\|like` | 2 h | Añadir en `app/config.py` y enrutar en `app/api/routes.py`. Rollback instantáneo |
| **[P0-2]** Suite de relevancia canónica (`tests/data/search_queries.json`, ≥20 queries) + umbral Jaccard/Kendall | 4 h | Comparación top-10 entre backends. Bloqueante en CI |
| **[P0-3]** Dual-read de búsqueda en staging (log-only) + validación de umbral | 2 h | Exigir igualdad dentro del umbral antes de promover |
| **[P0-4]** Adaptador `SearchRepo` (`SqliteFtsRepo`, `PgTsvectorRepo`, `LikeRepo`) | 3 h | Desacopla SQL de los endpoints |

### Pre-Sprint P0-2 (11 h) — Datos locales + Operación (P0-9–P0-16)

| Tarea | Horas | Notas |
|---|---|---|
| **[P0-9]** Coexistencia lectura dual (localStorage + servidor) | 3 h | Nunca sobrescribir en silencio. Mostrar origen |
| **[P0-10]** Merge con resolución de conflictos (`updated_at` + bitácora) | 4 h | UI para resolver duplicados antes de consolidar |
| **[P0-11]** Migración `localStorage` con `--dry-run` + backup JSON | 2 h | Exige `--confirm`. Bloqueante |
| **[P0-12]** Pre-check de conflictos + gate en sync | 2 h | Bloquea migración si hay conflictos sin resolver |

### Tareas adicionales obligatorias (previas a producción)

| Tarea | Horas | Cuándo |
|---|---|---|
| **[P0-5–P0-8]** Trazabilidad de licencias (por fila), license firewall, gate ODbL, aislamiento NC-ND | 14 h | Integrar en Sprint 0 (no posponer). Crear `scripts/check_license_compat.py` en CI |
| **[P0-13]** Redis para rate limits + refresh tokens revocados | 4 h | Antes de múltiples réplicas (Sprint 4/Sprint 8) |
| **[P0-14]** Checkpoint de migración BD + rollback ensayado | 2 h | Antes de tocar producción (Sprint 3) |
| **[P0-15–P0-16]** DoD crítico + `docs/RISK_LOG.md` | 2 h | Al cerrar Fase 0b |

**DoD FASE 0b:** Gates CI activos (`license-check`, `search-relevance-threshold`, `migration-dry-run`), feature flags con fecha de caducidad definida, rollback probado. Solo entonces pasar a Sprint 0.


### Sprint 0 — Licencias (11 h) · BLOQUEANTE
- **Objetivo**: decidir qué datos pueden sostener un negocio, por escrito.
- Inventario de fuentes con licencia real y URL de la licencia (3 h)
- Marcar y **excluir del pipeline comercial** las fuentes NC (2 h)
- Decidir la estrategia de procedencia por campo: hecho curado propio vs texto verbatim (3 h)
- `ATTRIBUTION.md` generado desde el origen real (3 h)
- **Definido hecho**: un documento de una página que dice, para cada fuente, si es comercial o
  no y qué obligación impone. Sin él, N2 y S1 quedan bloqueados.
- **No hacer**: escribir código de migración todavía.

### Sprint 1 — PostgreSQL: decisión y esquema (11 h)
- **Objetivo**: que el destino de los datos esté decidido y sea reversible.
- ADR: Postgres gestionado (Render/Neon/Supabase) con coste mensual comparado (3 h)
- Migración de los 22 modelos con Alembic, entorno de staging (5 h)
- Detectar y apartar el SQL específico de SQLite (`ALTER TABLE`, `sqlite_master`, `SELECT 1 FROM products`) (3 h)
- **Definido hecho**: la app arranca contra Postgres en staging con el catálogo importado.
- **No hacer**: aún no cambies producción.

### Sprint 2 — Búsqueda en Postgres (11 h)
- **Objetivo**: reescribir la parte que bloquea la migración.
- `tsvector` generado en una columna, con configuración de idioma español e inglés (4 h)
- Índice GIN y función de *ranking* equivalente a `bm25()` (3 h)
- Probar relevancia con las búsquedas que la gente usa de verdad, a mano (2 h)
- Modo degradado (`LIKE`) como red de seguridad durante la transición (2 h)
- **Definido hecho**: búsqueda relevante con y sin acentos y en ambos idiomas, y tests que
  comparan los resultados con los de SQLite.
- **No hacer**: no optimices ranking más allá de «ordenado por relevancia».

### Sprint 3 — Infraestructura y datos (11 h)
- **Objetivo**: que producción deje de perder datos.
- Postgres gestionado con PITR y staging real (4 h)
- Migración de los 4.259 productos y verificación de conteos (3 h)
- Backup y **restore ensayado** con.datetime exacto (3 h)
- Secretos por entorno, incluido `SECRET_KEY` (1 h)
- **Definido hecho**: restaurar un backup y recuperar un lote escrito después del último dump.

### Sprint 4 — Identidad: verificación y recuperación (11 h)
- **Objetivo**: que una cuenta se pueda recuperar y no se pueda suplantar.
- Verificación de email con token de un solo uso y expiración (4 h)
- Reset de contraseña con token y sesión única (4 h)
- Invalidar refresh tokens al cambiar la contraseña (2 h)
- Tests de los tres flujos (1 h)
- **Definido hecho**: un usuario puede registrarse, verificar, hacer reset y volver a entrar.

### Sprint 5 — Sesiones y datos personales (11 h)
- **Objetivo**: cumplir la parte de datos que ya aplica desde el primer usuario real.
- Gestión de sesiones activas y «cerrar todas» (3 h)
- Export de todos los datos del usuario (3 h)
- Borrado de cuenta con consecuencia clara sobre lotes y reseñas (3 h)
- ToS y privacidad redactados (2 h)
- **Definido hecho**: el usuario puede exportar y borrar su cuenta sin intervención del admin.

### Sprint 6 — Moderación operativa (11 h)
- **Objetivo**: convertir el booleano `flagged` en un proceso.
- Cola de reportes con estado: pendiente, en revisión, resuelto, descartado (4 h)
- Rol admin con bitácora de quién resolvió qué (3 h)
- Filtro automático mínimo: cuentas nuevas no pueden publicar de inmediato (2 h)
- Panel de moderación mínimo (2 h)
- **Definido hecho**: un reporte se resuelve, queda registrado y desaparece de la vista pública.
- **No hacer**: no construyas ML de moderación. Con 5,6 h/semana, la moderación manual es
  suficiente hasta que duela.

### Sprint 7 — Playwright (11 h)
- **Objetivo**: recuperar la red de seguridad antes de que haya usuarios.
- Instalación, fixture de autenticación y BD de pruebas contra Postgres (3 h)
- E2E: crear lote → registrar checkpoint → marcar listo (4 h)
- E2E: buscar → detalle → publicar reseña → moderarla (2 h)
- Integración en CI con reintentos (2 h)
- **Definido hecho**: el flujo de moderación está en tests, no solo en tu cabeza.

### Sprint 8 — Caché y notificaciones (11 h)
- **Objetivo**: que los fixes lleguen y que la web se comporte como una app.
- `CACHE_NAME` con hash del build y fallo de CI si no cambia (3 h)
- Push notifications: permiso, suscripción y entrega (4 h)
- Notificación de fermentación lista (2 h)
- CORS cerrado, límites en auth y cabeceras de seguridad (2 h)
- **Definido hecho**: un fix de CSS llega a un usuario con la app instalada sin tocar nada.

### Sprint 9a — Lotes fuera del navegador: coexistencia + dry-run (11 h) · ANTES de Sprint 3
- **Objetivo**: que el dato del usuario viva en su cuenta.
- **[P0-9/P0-10/P0-11/P0-12]** Lectura dual, resolución de conflictos, dry-run + backup JSON y pre-check de migración (6 h)
- Antes de consolidar: **exportar `localStorage` a un archivo** (30 min, irrecuperable si se omite)
- Importador `pantry_timers` / `pantry_prod` → `/me/batches` (modo lectura dual) (3 h)
- Export del registro de lote en CSV (1,5 h)
- Indicación en la UI de origen (`local|server|merged`) (1 h)
- **Definido hecho**: dry-run sin pérdidas, conflictos detectados y lectura dual activa.

### Sprint 9b — Lotes fuera del navegador: consolidación tras migración (11 h)
- **Objetivo**: consolidar tras la migración a Postgres (Sprint 3).
- Ejecutar migración con `--confirm` tras pasar gates (3 h)
- Resolver conflictos detectados en 9a vía UI (4 h)
- Tests E2E de migración (2 h)
- Validar integridad y limpiar datos temporales (2 h)
- **Definido hecho**: migración exitosa con rollback probado.

### Sprint 10 — Contenido de comunidad (11 h)
- **Objetivo**: que un usuario tenga algo que compartir.
- Perfil público con lotes visibles (4 h)
- Fotos de lote con cámara y subida (3 h) — con moderación de imágenes
- Flujo de invitación y enlace de compartir (2 h)
- Empty states y onboarding «tu primer fermento» (2 h)
- **Definido hecho**: un usuario puede publicar su fermentación y compartirla con un enlace.
- **No hacer**: follows, likes y comentarios. Aún no hay masa crítica para que signifiquen algo.

### Sprint 11 — Operación y datos de uso (11 h)
- **Objetivo**: que un fallo sea visible y reversible.
- Alerta de antigüedad del snapshot y de fallo de ingesta (3 h)
- Runbook: «el artefacto está obsoleto», «la ingesta falló», «Postgres no conecta» (3 h)
- Métricas de uso: registros, lotes publicados, reseñas, retención (3 h)
- CHANGELOG y notas de release (2 h)
- **Definido hecho**: puedes responder «¿cuánta gente usa esto?» con un dato.

### Sprint 12 — Refactor de `app.js` (11 h)
- **Objetivo**: dejar de editar un monolito antes de que toque cinco dominios.
- Extraer lotes, catálogo y reseñas a dominios propios (6 h)
- CSS inline residual a clases (3 h)
- Tests verdes en todo momento (2 h)
- **Definido hecho**: `app.js` baja de 188 KB.

### Sprint 13 — Decidir el siguiente ciclo (11 h)
- **Objetivo**: elegir la vía con datos, no con opinión.
- Comparar comunidad, comercial y app con las métricas del Sprint 11 (3 h)
- Escribir el ADR de la bifurcación (sección 4) (3 h)
- Recortar el backlog a lo que sostiene esa decisión (3 h)
- Cerrar o mover lo que no entre (2 h)
- **Definido hecho**: hay un plan de 6 meses para la vía elegida, con Must y Won't.

---

## 4. La bifurcación: qué sigue después del Sprint 14

La fundación sirve a las tres vías. Lo que se añada depende de cuál vaya primero, y esa es la
decisión que conviene tomar con el ADR del Sprint 13, no ahora.

### Si va primero la comunidad
- Perfiles y follows, moderación de imágenes con cola
- Flujo de invitación y growth loop
- Contenido generado por usuarios como activo principal
- **Coste que hay que asumir**: moderación y soporte son trabajo recurrente. A 5,6 h/semana,
  un máximo cómodo es del orden de cientos de usuarios activos, no miles.

### Si va primero lo comercial
- Billing y entitlements, cuotas por plan, factura y fiscalidad
- Soporte y límites de uso
- **Coste que hay que asumir**: vender exige ventas, soporte y un nivel de servicio que nadie
  tiene todavía. Se puede vender acceso a la API o licencia de datos sin comunidad.

### Si va primero la app
- Push, cámara y offline ya están en el Sprint 8-9
- Probar si la PWA retiene a un usuario semanal antes de invertir en una nativa
- **Coste que hay que asumir**: el ciclo de release de un store es más lento y menos reversible.
  Para 5,6 h/semana, esa fricción se nota.

**Recomendación, por si sirve**: comunidad antes que comercial. El conocimiento del dominio
está construido (los 30 ítems de datos ya construidos son el activo real), mientras que vender sin
usuarios reales no es solo más lento: es que no se puede corregir. La monetización puede
vivir sobre una comunidad pequeña —planes de API, licencia de datos, funciones premium—
sin necesidad de facturar desde el día uno.

---

## 5. Reglas de trabajo

1. **Regla de las 5,6 h**: si un sprint no cierra, se recorta alcance; no se alarga el sprint.
   El backlog se respeta.
2. **Nada nuevo empieza sin un Must cerrado.** Cada Must es una barrera para abrir la siguiente.
3. **Cada arreglo entra con su test** en el mismo commit. Sin equipo, esa es toda la red.
4. **Una sesión, un tema**, con nota de siguiente acción al cerrar.
5. **El roadmap solo se actualiza con números verificados**, y el bloque «Datos actuales» se
   regenera desde `/api/v1/stats`.
6. **Toda decisión de más de 4 h se escribe antes de empezar** (ADR de una página). Si no está
   escrita, a las tres horas se ha olvidado el porqué.
7. **El trabajo de comunidad tiene hora.** Si no cabe en el sprint, se aplaza una semana
7. **El trabajo de comunidad tiene hora.** Si no cabe en el sprint, se aplaza una semana declarada. Sin esto, los usuarios se comen el roadmap.
8. **Sin flags temporales sin fecha de caducidad.** Todo feature flag debe tener fecha de caducidad y eliminarse tras promover.
9. **Rollback probado.** Toda migración crítica debe tener script de rollback ensayado en staging.
10. **Gates obligatorios.** `license-check`, `search-relevance-threshold` y `migration-dry-run` deben pasar en CI antes de promover.

---

## 6. Lo que este plan NO cubre

- **Cuándo se empieza a ganar dinero.** No está aquí. Depende de la bifurcación y de tener
  usuarios; el Sprint 13 solo decide el orden, no la fecha.
- **Fiscalidad y entidad legal.** Necesario antes de cobrar, no antes de construir.
- **Si las 5,6 h/semana bajan a 3**, los 14 sprints se convierten en 24-26. La secuencia sigue
  válida; solo se alarga.
- **El coste mensual de Postgres gestionado** es una factura recurrente que conviene mirar
  antes del Sprint 3.