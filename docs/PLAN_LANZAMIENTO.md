# Plan de lanzamiento — auditoría del roadmap

Análisis de dirección de proyecto sobre `ROADMAP.md` y el estado real del repositorio.
Fecha: 2026-10-03. Alcance: qué falta antes de tratar el proyecto como lanzable.

> Este documento **no sustituye** al roadmap: lo ordena. El roadmap dice qué construir;
> este dice qué impide que eso sobreviva al uso real.

---

## Veredicto

El proyecto tiene construida la capa de producto (~85%) y casi toda la capa operativa (~30%).

Tres decisiones bloquean el resto:

| # | Decisión | Por qué bloquea |
|---|---|---|
| 1 | **Almacenamiento**: ¿disco persistente o PostgreSQL? | Toda la Fase 4 escribe datos de usuario; hoy viven en disco efímero |
| 2 | **Licencias**: ¿se publica el dataset? ¿el proyecto es comercial? | La API pública y el servidor MCP ya redistribuyen datos mixtos |
| 3 | **Audiencia**: ¿directorio de catálogo, comunidad o herramienta profesional? | Determina inversión en UGC, SEO, moderación e i18n |

El roadmap tiene 833 líneas y 12 preguntas sin responder. No es un documento de planificación,
es un catálogo de ideas. Estas tres respuestas lo convierten en uno.

---

## 1. Bloqueantes técnicos

### 1.1 No hay persistencia de datos en producción

No figura en ninguna fase. Es la condición de posibilidad de auth, lotes, reseñas y recetas.

- `render.yaml`: `plan: free` y **sin `disk`** → sistema de ficheros efímero.
- `buildCommand` restaura una BD prefabricada desde el último release de GitHub
  (`ingest/restore.py`), con *fallback* a la ingesta completa.
- El último release es `db-snapshot-2026-08-24`.
- `app/services/stats_service.py` describe la BD como "de solo lectura en producción",
  aunque no hay ninguna guarda de solo lectura en el código (`grep read_only` → 0 resultados).

**Efectos:**

| Efecto | Detalle |
|---|---|
| Pérdida de datos de usuario | Cada reinicio re-descarga el snapshot → `users`, `batches`, `reviews`, `recipes`, `producers`, `api_keys` se vacían |
| Sesiones inválidas | El secreto JWT se genera en `data/.jwt_secret` (efímero) → se regenera en cada despliegue |
| `5.2` Refresh inoperante | Lo que escriba el scheduler muere con la instancia; no hay ruta al usuario |
| `5.3` Caché inválida | "Dict TTL en memoria" solo vale con una instancia y sin reinicios (igual que el rate limiting, `app/main.py:149-151`) |

**Acción**: separar la BD de catálogo (artefacto descargable, solo lectura) de la BD de usuario
(nunca del release), elegir almacenamiento con disco y ensemblesajar backup y restore.

### 1.2 La invalidación de caché del PWA es manual

`app/static/sw.js` sirve **cache-first para todos los GET**. El único mecanismo de
invaliación es `CACHE_NAME = "conservas-world-v10"`, que se sube a mano.

Los commits de accesibilidad `0bd4091` y `57d8c83` no lo tocaron: cualquier usuario con la PWA
instalada sigue recibiendo el CSS y el JS anteriores. Con `curl` no se detecta, porque ignora
el service worker.

**Acción**: versionar `CACHE_NAME` con el hash del build + checklist de release.
De paso, estrategia diferenciada: cache-first para estáticos versionados, network-first para `/api/*`.

### 1.3 Cifras del roadmap no reproducibles

| Fuente | Productos |
|---|---|
| `GET /api/v1/stats` en producción | 4.259 |
| `data/build.db` local, `status != 'discarded'` | 4.259 |
| `data/build.db` local, todas las filas | 10.415 (6.156 `discarded`, 4.229 `imported`, 30 `active`) |
| `ROADMAP.md` línea 16 | «6.152 productos activos» |

Producción y repositorio coinciden; **la cifra del roadmap simplemente no se reproduce**
(un 30% por encima). Las 6.156 filas descartadas explican casi con exactitud el número citado,
lo que sugiere que se confundió el total con el activo. Cualquier decisión de producto tomada
sobre esa cifra (cobertura de mercado, prioridad de categorías, comparación competitiva) parte de un número inventado.

**Acción**: regenerar el bloque "Datos actuales" del roadmap desde el propio `/api/v1/stats`.

### 1.4 Los datos publicados sin resolver la propiedad intelectual

Las preguntas 8 y 12 del roadmap siguen abiertas, pero la API pública (3.9) y el servidor
MCP (3.10) ya redistribuyen el dataset.

- `LICENSE` es MIT (código), pero la BD mezcla **ODbL** (Open Food Facts),
  **CC BY-SA** (Wikipedia, DBpedia), **CC BY** (FermDB, FDF-DB) y **CC BY-NC-ND** (FermFooDb).
- ODbL y CC BY-SA son copyleft: publicar el dataset derivado puede imponer obligaciones sobre
  el conjunto, y el MIT del código no las cancela.
- **No existe `ATTRIBUTION.md`**, aunque el roadmap enumera los requisitos por fuente.
- **2.4 (FermFooDb)** es el peor caso: *No Derivatives*. Una fila de péptido emparejada por
  nombre **es** un derivado.

**Acción**: matriz de compatibilidad de licencias, decisión explícita sobre carácter comercial,
y `ATTRIBUTION.md` generado desde el origen real de cada dato.

### 1.5 Nadie es dueño de la frescura de los datos

`5.4` monitoriza latencia y errores de la app, no del pipeline. Nadie recibe un aviso de que
producción sirve un snapshot de seis semanas. Debería existir un SLO de frescura
(`snapshot_age_days`) con alerta, y el release de BD debería salir de un workflow, no de una
subida manual.

---

## 2. Dependencias rotas

| Contradicción | Efecto |
|---|---|
| 3.1 batch tracking "requiere auth (4.1)", pero el orden pone 3.1 en semana 10-12 y auth en el mes 4 | Hoy vive en `localStorage`; no hay ruta de migración, el usuario pierde sus lotes al cambiar de dispositivo |
| `5.2 Refresh ✅` con restauración por artefacto | Inoperante en producción |
| `5.3 Caché` y rate limiting en memoria | Impide escalar a más de una instancia |
| `4.7 PWA` depende de push y de bumpear el SW | No hay proceso que lo haga |
| `4.9 SEO` asume "vanilla SPA" y a la vez pide prerender de ~4.700 páginas | Conflicto de arquitectura sin decidir; el prerender es el canal de adquisición de un catálogo |
| `4.8 i18n` depende de aliases de 2.16, marcado "pendiente futura" | Dependencia circular suave |
| `3.4 Guías` para "los 50 más populares" | No hay definición de "popular": no existe analítica de producto |

---

## 3. Fases de investigación que faltan

- **0 investigación de usuario**: 0 entrevistas, 0 tests de usabilidad, 0 analítica de producto
  (`5.4` mide latencia y errores; no embudos, ni uso por feature, ni retención).
- **Legal**: matriz de compatibilidad de licencias (hoy solo hay una lista), responsabilidad
  sobre consejos de seguridad alimentaria (pH, aw y vida útil son afirmaciones de salud pública),
  RGPD (exportar/borrar datos, privacidad) y si el proyecto es comercial.
- **Accesibilidad**: `4.10` es una casilla. Falta investigación con usuarios con discapacidad y
  la auditoría con axe-core (la dependencia está en la tabla del roadmap y nunca se añadió).
  Falta también el coste recurrente: cada `style="..."` inline en una plantilla JS puede volver
  a romper el contraste sin que nada lo detecte.
- **Calidad de datos**: no hay procedencia ni confianza por campo, ni mecanismo para reportar un
  producto inexacto. `tests/test_data_integrity.py` fija suelos agregados, no verificabilidad.
- **Riesgo operativo**: no existe runbook para "el artefacto está obsoleto" ni "la ingesta falló
  en el deploy" — el *fallback* a ingesta completa ya falló antes por 429 a IP de datacenter.
- **Coste y plataforma**: Render free no tiene disco; el MCP siempre vivo y la búsqueda
  semántica (~80MB de modelo) no caben en ese plan.

---

## 4. Lo que falta desde la perspectiva del usuario

### Primer contacto
- Sin onboarding ni ruta guiada: 4.259 productos sin jerarquía. Las guías (3.4) cubren 50.
  Falta un "tu primer fermento en 7 días".
- Sin estados vacíos diseñados para Despensa, favoritos y listas.

### Búsqueda
- Sin conteos por faceta, sin "quizás querías decir", sin criterio de orden explicable.
- Sin URL de estado: compartir una búsqueda es imposible.
- Sin feedback AND/OR al combinar filtros.
- La búsqueda semántica (3.5) no tiene interfaz: no se comunica qué puede preguntar ni en qué
  se diferencia de la literal.

### Detalle y confianza
- Hay ~4.900 referencias pero **no se citan junto a cada dato**. El usuario no puede distinguir
  si "12 meses de vida útil" es dato curado o heurístico. Falta procedencia visible y fecha de
  última verificación.
- El detalle de ingrediente muestra alias en 10 idiomas sin indicar qué está traducido: el
  usuario internacional obtiene una experiencia parcialmente inglesa sin señal alguna.

### Seguridad alimentaria
- Sin disclaimers, sin "consulta a un profesional", sin advertencias de alérgenos por defecto.
- La calculadora de altitud (3.2) no advierte de que las tablas asumen condiciones concretas.
- Sin advertencia de alérgenes cruzados en la lista de la compra.

### Lotes y temporizadores
- Es la feature de retorno frecuente y la más frágil: sin modo offline real, sin flujo de
  permiso de notificaciones, sin sincronización de checkpoints sin conexión y con riesgo de
  pérdida al cambiar de dispositivo.
- Los temporizadores no sobreviven a que el navegador descarte el estado.

### Comunidad
- "Flag de contenido" sin cola de moderación, sin estados visibles y sin flujo de reportar.
- Sin "mis contribuciones", sin avatar, sin edición.
- El registro de productores abre riesgos de verificación y de datos de contacto sin proceso.

### Transversal
- Errores de carga hardcodeados en español dentro de plantillas JS, incoherentes con el cambio
  de idioma.
- Sin política de privacidad, sin exportar/borrar mis datos, sin consentimientos.
- Sin sistema de estados de carga/vacío/error: se han ido resolviendo botón a botón.

---

## 5. Hitos técnicos antes del lanzamiento

### Testing
- **Nada de pruebas de navegador.** ~187KB de `app.js` y 68KB de CSS se validan con
  aserciones de texto sobre el código fuente. El gestor de foco de overlays
  (`initOverlayA11y`) está "cubierto" por tests que solo comprueban que la cadena existe:
  un selector mal escrito rompe los 20 modales y CI pasa.
- **E2E con Playwright** para los 5 flujos: buscar→detalle, crear lote→checkpoint→listo,
  registro/login, reseña, lista de la compra.
- **axe-core en CI** sobre las páginas reales (dependencia pendiente desde hace meses).
- **Regresión visual** en lo que cambió con el trabajo de accesibilidad: contraste claro/oscuro,
  variantes de etiqueta, drawer móvil.
- Presupuesto de rendimiento (LCP con mapa Leaflet + Chart.js + D3).
- Matriz de CI con varias versiones de Python, más `pip-audit`, Dependabot y CodeQL.

### Refactorización
- Extraer el CSS inline de las plantillas JS a clases: es la causa raíz del contraste frágil.
- Extraer los strings hardcodeados de las plantillas al diccionario i18n.
- **Dividir `app.js`**: 187KB monolíticos donde cada feature toca un archivo que todos tocan.
  Por dominio: catálogo, lotes, reseñas, mapa, paleta.
- Sacar el dump binario de 9,7MB del repositorio git; los datos como artefacto de release.
- Revisar el arranque en frío de Render free con SQLite.

### Seguridad
- **CORS `allow_origins="*"` con `allow_credentials=True`** (`app/main.py:88-95`) y
  `render.yaml` sin definir `CONSERVAS_CORS_ORIGINS`. El comentario dice "restringir en
  producción" y producción no lo restringe.
- **Rate limiting global en memoria**: falta límite específico en `/auth/login`,
  `/auth/register`, `/recipes` y `/reviews`, y lista de hosts permitidos.
- **Rotación de `SECRET_KEY` e invalidación de refresh tokens**: sin lista de revocación no se
  puede cortar una sesión comprometida.
- Validación de subidas cuando lleguen las fotos de checkpoints (3.1) y recetas (4.3):
  bytes reales, tamaño, EXIF.
- `SECURITY.md` y canal de reporte de vulnerabilidades.
- Cabeceras de seguridad: no hay CSP ni Helmet.
- Auditoría de permisos sobre `/me/*` y revocación de API keys.

### Operaciones
- Persistencia, backup y restore probado (ver 1.1).
- PostgreSQL si habrá comunidad real: SQLite con un único escritor no da para eso.
- Alertas de frescura del snapshot, fallo de ingesta y salud del MCP.
- Runbook, CHANGELOG, versionado y notas de release. El roadmap dice "512 tests" y hay 600:
  el documento no se mantiene y nadie tiene asignada esa tarea.

---

## 6. Plan de acción

### Esta semana

| # | Acción | Por qué |
|---|---|---|
| 1 | Decidir almacenamiento y separar la BD de usuario del artefacto de catálogo | Bloquea toda la Fase 4 |
| 2 | Versionar `CACHE_NAME` con el hash del build + checklist de release | Arregla hoy a los usuarios con PWA |
| 3 | Cerrar CORS y añadir límites a los endpoints de auth | Ventana abierta en producción |
| 4 | Escribir la matriz de licencias y crear `ATTRIBUTION.md` | Obligation legal latente |
| 5 | Meter Playwright con dos flujos (lote y búsqueda→detalle) | Mayor riesgo técnico abierto |

### Antes de anunciar nada
- Regenerar las cifras de "Datos actuales" desde `/api/v1/stats`.
- axe-core en CI + regresión visual en ambos temas.
- Runbook de despliegues y de fallo de ingesta.
- Corregir los recuentos obsoletos del roadmap (tests, productos).

---

## 7. Preguntas que el roadmap debe responder

Las 12 preguntas del apartado final están bien planteadas pero sin decidir. Las que
desbloquean trabajo:

1. ¿El proyecto es comercial? Determina si caben `CC BY-NC` (FermFooDb, FooDI-ML, Flavor Network).
2. ¿Se publica el dataset como open data? Si sí, bajo qué licencia y con qué atribución.
3. ¿Almacenamiento: disco persistente o PostgreSQL? De esto depende si la Fase 4 es viable.
4. ¿Audiencia: directorio de catálogo, comunidad o herramienta profesional? Define la
   inversión en moderación, SEO e i18n.
5. ¿Se acepta contenido bajo NC-ND, o se excluye? Afecta a 2.4.