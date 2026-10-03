# MoSCoW, cuellos de botella y sprints

Plan de ejecución derivado de la auditoría de lanzamiento.

- **Parámetros**: 5-6 h/semana, trabajo en solitario.
- **MVP definido como**: herramienta personal de fermentación (catálogo + lotes + temporizadores + calculadoras).
- **Fecha**: 2026-10-03.
- **Complementa** a `ROADMAP.md` (qué construir) y `docs/PLAN_LANZAMIENTO.md` (qué impide lanzarlo).

---

## 0. Punto de partida: el problema ya no es construir

El roadmap tiene **26 de 31 ítems completados**. Las Fases 1, 3 y 4 están prácticamente
enterras; de la Fase 2 solo quedan 5 integraciones de datos; la Fase 5 está a medias.

Con 5,6 h/semana ≈ **285 h/año**, el trabajo restante no puede crecer. El objetivo de este
plan no es priorizar el backlog: es **recortarlo hasta que quepa**, y que lo que ya está
construido deje de romperse.

Corolario: la mayor parte del MoSCoW de abajo es «no hacer», no «hacer».

---

## 1. Matriz MoSCoW

### Must have — sin esto no hay MVP

Un MVP de herramienta personal que pierde los lotes en cada reinicio y no llega a los
usuarios con la PWA instalada no es un producto: es una demo.

| # | Ítem | Por qué es imprescindible | Esfuerzo |
|---|---|---|---|
| M1 | **0.1 Persistencia de datos** | `plan: free` sin `disk` + restauración desde artefacto ⇒ cada reinicio borra usuarios, lotes y sesiones. El lote **es** el producto | 2-4 h si hay disco |
| M2 | **0.2 Invalidación de caché automatizada** | El SW sirve cache-first y solo se invalida a mano. Sin esto, M1 y todos los arreglos anteriores no llegan a quien tiene la PWA | 2-3 h |
| M3 | **Migrar `pantry_timers`, `pantry_prod`, `pantry_favs` a la cuenta** | Hoy viven solo en `localStorage`: se pierden al cambiar de dispositivo o al limpiar el navegador. Es el corazón de la herramienta personal | 6-8 h |
| M4 | **Export del registro de lote (CSV)** | El usuario necesita llevarse sus datos. Hoy el export solo existe para productos | 3 h |
| M5 | **0.4 CORS + rate limit en auth + cabeceras** | `allow_origins="*"` con `allow_credentials=True` en producción | 5-6 h |
| M6 | **Verificación en navegador (Playwright, 2 flujos)** | Sin nadie más, los tests de texto son la única red y no detectan un selector roto. Es la compra que evita perder el día en un bug invisible | 6-8 h |
| M7 | **Copia de seguridad y restore ensayados** | Un backup no probado no es un backup | 4-5 h |
| M8 | **`ATTRIBUTION.md` + decisión de licencias** | Uso personal y no comercial cambia qué datasets son admisibles, pero la atribución es obligatoria igual (ODbL, CC BY-SA, CC BY) | 3-4 h |
| M9 | **Temporizadores fiables** (notificación, sobreviven recarga, offline) | Si el temporizador falla, la herramienta no cumple su función | 6-8 h |
| M10 | **0.6 Corregir cifras del roadmap** | 10 minutos y elimina un número inventado en el documento rector | 0,5 h |

**Total Must: ~40-50 h ≈ 9-10 sprints de 2 semanas.**

### Should have — Improves the tool without blocking it

| # | Ítem | Esfuerzo | Nota |
|---|---|---|---|
| S1 | axe-core en CI | 3 h | La dependencia está en el roadmap desde hace meses y nunca se añadió |
| S2 | Alertas de frescura del snapshot y de fallo de ingesta | 3 h | Sin esto nadie detecta que producción sirve un release de hace semanas |
| S3 | Empty states y onboarding mínimo | 5 h | «Tu primer fermento»: hoy no hay nada que guíe al usuario nuevo |
| S4 | Dividir `app.js` por dominio | 8 h | 188KB monolíticos; precondición para editar con seguridad |
| S5 | CSS inline y strings hardcodeados fuera de las plantillas | 5 h | Causa raíz del contraste frágil |
| S6 | Runbook de despliegue y de fallo de ingesta | 3 h | El fallback a ingesta completa ya falló por 429 |
| S7 | `SECRET_KEY` por entorno con rotación y revocación de refresh | 3 h | Sin revocación no se corta una sesión comprometida |
| S8 | CHANGELOG y notas de release | 2 h | El roadmap dice «512 tests» y hay 600: el documento sin dueño se pudre |

### Could have — Cuando haya margen

| # | Ítem | Por qué no ahora |
|---|---|---|
| C1 | FlavorDB y pairing por compuestos (2.12) | 193 mapeos curados a mano; valor de Leave |
| C2 | Microbioma profundo (2.2) | Parsing académico con poco retorno para un usuario que fermenta en casa |
| C3 | Regresión visual completa | Espera a que Playwright esté en marcha; antes es trabajo desperdiciado |
| C4 | Export PDF de recetas | CSV cubre el caso de uso real |
| C5 | Monitorización de producto (uso por feature, embudos) | Útil para decidir, no para lanzar |

### Won't have — Explícitamente fuera de este ciclo

Cada uno de estos ítems es trabajo real. A 5,6 h/semana, decir «no» es la decisión que
protege el MVP.

| # | Ítem | Motivo |
|---|---|---|
| W1 | **2.4 Péptidos bioactivos** | Licencia CC BY-NC-ND: emparejar una fila por nombre *es* un derivado. Bloqueo legal + valor cero para una herramienta personal |
| W2 | **2.5 Ontología FoodOn** | Interoperabilidad sin usuario que la pida |
| W3 | **2.8 Open Wine Map** | Solo Europa; el mapa actual ya cumple |
| W4 | **3.7 Integración Fermentor.org** | Requiere una licencia que no está verificada |
| W5 | **4.8 i18n a 10 idiomas** | ES/EN basta para uso personal; 500 strings por idioma no son 5,6 h/semana |
| W6 | **4.9 SEO y prerender** | Solo tiene sentido con audiencia pública. Es la decisión nº4 del plan de lanzamiento |
| W7 | **React Native** | Multi-dispositivo, no multipROYECTO |
| W8 | **Moderación de comunidad** | Revis 4.2/4.3/4.6 están construidas pero congeladas: sin moderationtooling no se invierte más ahí |
| W9 | **Optimización de la API pública y API keys** | Ya funciona; sin terceros que la usen no se toca |
| W10 | **PostgreSQL** | Ver cuellos de botella: no es el camino para una herramienta personal |

### Done — Congelado

Solo tests de regresión. No se aceptan features nuevas sobre estas piezas:

`1.1` nutrición USDA · `1.2` ruff+mypy+CI · `1.3` dark mode · `1.4` autocomplete · `1.5` estacional ·
`1.6` export productos · `1.7` etiquetas de dieta · `1.8` glosario · `2.1` mapa · `2.3` pH/seguridad ·
`2.6` Ark of Taste · `2.7` cervecerías · `2.9` etimología · `2.10` cronología · `2.11` imágenes ·
`2.13` lácteos FDF-DB · `2.14` África/Oriente Medio · `2.15` shelf-life · `2.16` LanguaL ·
`3.2` calculadoras · `3.3` pairings · `3.5` búsqueda semántica · `3.6` mapa de sabores ·
`3.8` temporizadores por temperatura · `3.9` API pública · `3.10` MCP · `4.1` auth ·
`5.1` Alembic · `5.2` refresh

> Nota: `3.5` está implementada con **TF-IDF propio**, sin sentence-transformers ni FAISS.
> El roadmap la estimaba en ~80MB de modelo; el coste real es casi cero. Se corrige aquí.

---

## 2. Cuellos de botella

Ordenados por probabilidad de complicarse × impacto si se complica.

| # | Cuello | Prob. | Impacto | Esfuerzo si falla |
|---|---|---|---|---|
| B1 | **Almacenamiento (M1)** | Alta | Muy alto | 2-4 h (disco) o 20-40 h (Postgres) |
| B2 | **Migrar `localStorage` a la cuenta (M3)** | Alta | Alto | 6-8 h, y los lotes existentes del usuario se pierden si se pospone |
| B3 | **Playwright (M6)** | Media-alta | Alto | Curva de aprendizaje + tests frágiles; un dev solo tiende a abandonar esta tarea |
| B4 | **Olvidar bumpear la caché del SW (M2)** | Media | Medio-alto | Los arreglos no llegan; el fallo es invisible en `curl` |
| B5 | **Decisión de licencias (M8)** | Baja (técnica) | Alto | Bloquea la publicación; es decisión, no código |
| B6 | **Ancho de banda de 5,6 h/semana** | Certísima | Alto | El riesgo sistémico: 2-3 sesiones por semana, cada cambio de tema cuesta ~30 min |
| B7 | **FTS5 atado a SQLite** | Baja | Medio | Si se elige Postgres, la búsqueda se reescribe: `products_fts MATCH` y `bm25()` son SQL crudo |

### B1 en detalle: por qué disco y no Postgres

La decisión parece technique pero es de tiempo. El coste de Postgres no es la migración de
esquema: es que la **búsqueda es SQL crudo de FTS5** (`app/api/routes.py:101`, `bm25()`).
Migrar a Postgres obliga a reescribir la búsqueda con `tsvector`/`pg_trgm`, reindexar y
revalidar relevancia. Hay un fallback (`_fts_matches` devuelve `None` si FTS5 falla) que
degrada a `LIKE`, así que no es catastrófico: se pierde ranking y velocidad.

Para una herramienta personal con un solo usuario, SQLite con disco persistente resuelve el
problema en 2-4 horas. Postgres solo se justifica si el objetivo pasa a ser comunidad, que
es la decisión nº4 del plan de lanzamiento y no la Actual.

### B2 en detalle: los datos del usuario están en el navegador

`pantry_timers`, `pantry_prod` y `pantry_favs` viven en `localStorage` (30 llamadas en
`app.js`). Hay sync a `/me/batches` cuando hay sesión, pero **no existe importador**: si el
usuario tiene lotes reales en su navegador ahora, hay que sacarlos a un archivo antes de tocar nada,
o se pierden. Esta es la tarea con más riesgo dezanja de la lista, porque el daño es
irreversible.

Mitigación: exportar `localStorage` a un archivo antes de migrar. Minuto y medio de trabajo
que evita perder datos.

### B6 en detalle: el cuello real

Con 2-3 sesiones semanales, el mayor coste no es el trabajo: es **volver al contexto**. Un
sprint de 11 h queda dividido en tres sesiones de menos de 4 h cada una.

Reglas que lo atacan:

1. **Una sesión, un tema.** Tres sesiones, tres temas. Nunca “un poco de todo”.
2. **Nota de siguiente acción al cerrar cada sesión.** Una línea: «Siguiente: M3 paso 2,
   migrar `pantry_timers` a `/me/batches`». Sin esto, la sesión siguiente se pierde 20 min
   releyendo.
3. **Todo fix entra con su test en el mismo commit.** Sin equipo, el test es la única red.
4. **Nada nuevo empieza sin cerrar un Must anterior.** Si un sprint se atasca, se recorta
   alcance; no se alarga el sprint.
5. **Trabajo largo en paralelo de verdade**: lanzar la suite de Playwright o una ingesta y
   mientras escribir documentación o tests. Es el único paralelismo real sin equipo.

### Cómo paralelizar en solitario

No hay paralelismo por personas, así que el paralelismo es **temporal y de contexto**:

| Situación | Técnica |
|---|---|
| Tarea bloqueante y larga (suite E2E, ingesta) | Lanzarla en segundo plano y avanzar en docs o tests |
| Dos tareas independientes y pequeñas | Una por sesión, nunca mezcladas |
| Cambios que se tocan entre sí (app.js) | Una sola sesión; partir el archivo antes (S4) |
| Trabajo administrativo (cifras, atribución, release notes) | Una sesión quincenal agrupada, no gotas repartidas |
| Tarea que exige contexto fresco (licencias, arquitectura) | Sesión completa, no 40 min robados |

---

## 3. Plan por sprints

**Formato**: sprints de 2 semanas, ~11 h por sprint (5,6 h/semana).
**Total**: 12 sprints ≈ 132 h ≈ **6 meses** hasta MVP utilizable.

Ningún sprint empieza con un Must sin cerrar.

### Sprint 1 — Blindaje y decisiones (11 h)
- **Objetivo**: que nada de lo ya arreglado se pierda, y fijar las dos decisiones que condicionan el resto.
- M2 · versionar `CACHE_NAME` con el hash del build y fallo en CI si no cambia (3 h)
- M10 · regenerar las cifras de «Datos actuales» desde `/api/v1/stats` (0,5 h)
- M8 · `ATTRIBUTION.md` generado desde el origen real de cada fuente (3 h)
- B1 · ADR de una página: disco persistente frente a Postgres, con el coste de FTS5 medido (2,5 h)
- Nota de siguiente acción y plantilla de sesión (2 h)
- **Definido hecho**: el build falla si `CACHE_NAME` no cambia; el roadmap no contiene cifras inventadas.
- **No hacer**: tocar features.

### Sprint 2 — Persistencia (11 h)
- **Objetivo**: que un reinicio no borre nada.
- M1 · contratar disco persistente, configurar `CONSERVAS_DATA_DIR` (3 h)
- M1 · separar la BD de usuario del artefacto de catálogo (3 h)
- M7 · backup automático diario con verificación de integridad (2 h)
- M7 · ensayo de restore en un entorno desechable (3 h)
- **Definido hecho**: crear un usuario y un lote, reiniciar la instancia, siguen ahí.
- **No hacer**: migrar a Postgres. Si el restore falla, se itera aquí.

### Sprint 3 — Los lotes del usuario (11 h)
- **Objetivo**: que el producto deje de depender del navegador.
- Antes de empezar: **exportar `localStorage` del usuario a un archivo** (30 min, irrecuperable si se omite)
- M3 · importador `pantry_timers` / `pantry_prod` → `/me/batches` (4 h)
- M3 · tests del importador, incluidos casos con datos corruptos (2 h)
- M3 · mostrar en la UI cuál es la fuente de verdad y avisar de la sincronización (2 h)
- M4 · export CSV del registro con checkpoints (2,5 h)
- **Definido hecho**: un lote creado sin cuenta aparece en la cuenta al iniciar sesión; el CSV incluye los checkpoints.

### Sprint 4 — Seguridad de producción (11 h)
- **Objetivo**: cerrar lo que está abierto.
- M5 · CORS restringido a orígenes conocidos, `CONSERVAS_CORS_ORIGINS` en Render (1 h)
- M5 · límites propios en `/auth/login`, `/auth/register`, `/recipes`, `/reviews` (3 h)
- M5 · cabeceras de seguridad y CSP mínima (2 h)
- S7 · `SECRET_KEY` por entorno, rotación y revocación de refresh tokens (3 h)
- S8 · `SECURITY.md` (2 h)
- **Definido hecho**: tests que demuestren `429` en login y que un origen ajeno recibe `403` de CORS.

### Sprint 5 — Playwright: el flujo de lote (11 h)
- **Objetivo**: recuperar la red de seguridad que un dev solo no tiene.
- M6 · instalación, fixture de autenticación y BD de pruebas (3 h)
- M6 · E2E: crear lote → registrar checkpoint → marcar listo (4 h)
- M6 · E2E: buscar → detalle → volver al listado (2 h)
- M6 · integración en CI con reintentos (2 h)
- **Definido hecho**: los dos flujos en CI; un fallo bloquea el merge.

### Sprint 6 — axe-core y seguridad de dependencias (11 h)
- **Objetivo**: que la accesibilidad no dependa de que nadie se acuerde.
- S1 · axe-core en CI sobre `/`, un detalle y un modal abierto (3 h)
- Corregir lo que aparezca (4 h)
- `pip-audit` y Dependabot (2 h)
- Revisión visual manual de los cambios de contraste en claro y oscuro (2 h)
- **Definido hecho**: CI falla ante una violación seria de axe.

### Sprint 7 — Temporizadores fiables (11 h)
- **Objetivo**: que la función principal de la herramienta no falle en silencio.
- M9 · notificación de temporizador finished con flujo de permiso (3 h)
- M9 · recuperar el estado tras cerrar y reabrir el navegador (3 h)
- M9 · comportamiento sin conexión (2 h)
- Tests de los tres casos (3 h)
- **Definido hecho**: el temporizador sobrevive a cerrar el navegador y avisa.

### Sprint 8 — UX de la herramienta personal (11 h)
- **Objetivo**: que un usuario sin datos sepa qué hacer.
- S3 · empty states de lotes, despensa y favoritos (3 h)
- S3 · recorrido mínimo «tu primer fermento» (4 h)
- S5 · errores de carga carrying al diccionario i18n (2 h)
- Revisión del flujo de lote en móvil (2 h)
- **Definido hecho**: un usuario nuevo ve un siguiente paso claro en la primera visita.

### Sprint 9 — Refactor de `app.js` (11 h)
- **Objetivo**: dejar de editar un monolito.
- S4 · extraer lotes, catálogo y reseñas a dominios propios (6 h)
- S5 · CSS inline residual a clases (3 h)
- Tests verdes tras cada extracción (2 h)
- **Definido hecho**: `app.js` baja de 188 KB; CI en verde en todo momento.

### Sprint 10 — Operación (11 h)
- **Objetivo**: que un fallo sea visible y reversible.
- S2 · alerta de antigüedad del snapshot y de fallo de ingesta (3 h)
- S6 · runbook: «el artefacto está obsoleto», «la ingesta falló», «la instancia no arranca» (3 h)
- S6 · ensayo completo de restore documentado con capturas (3 h)
- S8 · CHANGELOG y notas del primer release (2 h)
- **Definido hecho**: un fallo de ingesta genera alerta y el runbook dice qué hacer.

### Sprint 11 — Preparación del lanzamiento (11 h)
- **Objetivo**: decidir qué se enseña y qué se calla.
- Congelar alcance: ocultar o marcar las funciones de comunidad hasta que haya moderación (3 h)
- W8 · criterio de moderación documentado, aunque la herramienta no lo use todavía (2 h)
- Guía de uso de la herramienta (3 h)
- Checklist de lanzamiento firmada (3 h)
- **Definido hecho**: existe una lista firmada de qué entra en el MVP.

### Sprint 12 — Lanzamiento en frío (11 h)
- **Objetivo**: dos semanas de uso real sin pérdida de datos.
- Despliegue limpio desde cero, como lo vería un usuario nuevo (2 h)
- Smoke tests manuales de los 5 flujos (4 h)
- Monitorización daily durante la primera semana (3 h)
- Decidir el Won't-have del siguiente ciclo con datos de uso (2 h)
- **Definido hecho**: dos semanas de uso propio sin perder un lote ni una sesión.

---

## 4. Reglas de trabajo

1. **Regla de las 5,6 h**: si un sprint no cierra, se recorta alcance; no se alarga el sprint.
   El deuda se paga,spring se respeta.
2. **Nada nuevo empieza sin un Must cerrado.** Cada Must es una barrera para abrir la siguiente.
3. **Cada arreglo entra con su test** en el mismo commit. Sin equipo, esa es toda la red.
4. **Una sesión, un tema**, con nota de siguiente acción al cerrar.
5. **El roadmap solo se actualiza con números verificados**, y el bloque «Datos actuales» se
   regenera desde `/api/v1/stats`.
6. **Toda decisión de más de 4 h se escribe antes de empezar** (ADR de una página). Si no está
   escrita, a las tres horas se ha olvidado el porqué.

---

## 5. Lo que este plan NO cubre

- Si el objetivo pasa de herramienta personal a plataforma comunitaria, casi todo MoSCoW cambia:
  Postgres, moderación, i18n, SEO entran como Must y el plan se alarga a 12-18 meses.
- Costo mensual: el disco persistente de Render es una factura recurrente. Es el primer punto
  del que conviene ser consciente antes de dar el paso 1 del Sprint 2.
- Si las 5,6 h/semana bajan a 3, los 12 sprints se convierten en 20-22. La secuencia sigue
  siendo válida; solo se alarga.