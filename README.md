# Conservas del Mundo

Base de datos mundial de conservas, fermentos y encurtidos tradicionales: **6.182 productos** de 147 países con API pública, app web instalable (PWA), búsqueda semántica y servidor MCP para asistentes de IA.

[![CI Pipeline](https://github.com/Gintokisakat/conservas-world/actions/workflows/ci.yml/badge.svg)](https://github.com/Gintokisakat/conservas-world/actions/workflows/ci.yml)

## Stack

- **Backend**: Python 3.11 + FastAPI + SQLAlchemy 2.0
- **BD**: SQLite (FTS5 para búsqueda full-text), migrable a PostgreSQL
- **Ingesta**: pipeline automático desde fuentes abiertas (FermDB, Wikipedia, Open Food Facts, Wikidata, Ark of Taste, FDF-DB)
- **Frontend**: HTML/CSS/JS vanilla con i18n (ES/EN), Chart.js, Leaflet
- **IA**: servidor MCP (Model Context Protocol) con herramientas para asistentes

## Estructura

```
app/         → API FastAPI + modelos SQLAlchemy + frontend estático
app/services → dominio: timers, sabores, seguridad, curso, podcasts, etimología…
ingest/      → pipeline de ingesta, normalización y curaduría
mcp_server/  → servidor MCP para Claude y otros asistentes
data/        → descargas raw, datos de referencia, build.db (generada)
tests/       → suite pytest (322 tests)
```

## Comandos

```bash
uv sync                                    # instalar dependencias
uv run python -m ingest.ingest             # construir la base de datos (data/build.db)
uv run python -m ingest.ingest --reset     # reconstruirla desde cero
uv run uvicorn app.main:app --reload       # servir en http://localhost:8000
uv run pytest                              # ejecutar los tests
uv run ruff check . && uv run mypy app     # lint y tipos
```

Si `uv` no se encuentra: `export PATH="$HOME/.local/bin:$PATH"`.

Docs interactivas de la API: `http://localhost:8000/docs` · API pública documentada: [`docs/API.md`](docs/API.md)

### Docker

```bash
docker compose up --build   # app en http://localhost:8000
```

## Web app

La interfaz (sin framework, JS vanilla) se sirve en la raíz:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# Abrir http://localhost:8000
```

### Funcionalidades

**Exploración**
- Búsqueda con FTS5 + **búsqueda semántica** (TF-IDF, rankeo por similitud coseno) con sugerencias automáticas
- Filtros por categoría, continente, país, fuente, dieta, indicación geográfica y tiempo de fermentación
- **Mapa mundial interactivo** (Leaflet + OpenStreetMap) con clustering de productos
- Vista de lista o mapa, producto aleatorio ("Sorpréndeme")
- **Comparador de estadísticas** con gráficos (Chart.js): continente, fuente, categoría
- **Línea de tiempo histórica** de la fermentación y **glosario** (326 términos)

**Detalle de producto**
- Alias bilingües, países, ingredientes, microbios, referencias, sustrato y usos
- **Pairings** de sabor, **productos relacionados**, export JSON
- **Seguridad y pH predictivos** por tipo de fermento (rangos pH/aw/sal, alertas)
- **Temporizadores ajustados por temperatura** (modelo Q10) para saber cuándo está listo
- **Etimología** del nombre ("¿Sabías que…?") en productos emblemáticos
- Imágenes con atribución (Wikimedia Commons)

**Herramientas del fermentador**
- **Mi Despensa Interactiva**: qué podés *hacer* con tus ingredientes y qué podés *preparar* con tus fermentados (localStorage)
- Temporizadores F1/F2 con progreso, notas y ajuste por temperatura ambiente
- Calculadoras de salinidad y ABV, **guías paso a paso** (kimchi, chucrut, kombucha, miso, yogur) con temporizador por paso
- Diagnóstico visual de problemas (kahm, moho, salmuera turbia…) y enciclopedia de microbios
- Etiquetas imprimibles para frascos y lista de compras
- Favoritos y filtros guardados

**Educación y comunidad**
- **Curso de fermentación** con 5 módulos, progreso por lección y certificado imprimible
- **Índice de podcasts** (FermUp, Ferment Radio) filtrable por tema y fermento
- **Shelf-life** estilo FoodKeeper: cuánto dura cada ingrediente en nevera/congelador/despensa
- **Perfil de sabor por continente** (mapa de sabores)

**Plataforma**
- i18n completo ES/EN (UI y contenido), modo claro/oscuro
- **PWA instalable** con offline (service worker), iconos maskable y botón Instalar
- SEO: sitemap.xml (5.900+ URLs), robots.txt, SSR del detalle con Open Graph y JSON-LD
- Accesibilidad AA: landmarks, roles ARIA, focus visible, prefers-reduced-motion
- Rate limiting en la API pública con headers `X-RateLimit-*`

## API

Todas las respuestas son JSON. Documentación completa con ejemplos en [`docs/API.md`](docs/API.md). Resumen:

| Grupo | Endpoints |
|---|---|
| Productos | `GET /products`, `/products/{id}`, `/products/random`, `/products/dairy`, `/products/geo`, `/products/{id}/related`, `/pairings`, `/safety`, `/etymology`, `/export` |
| Búsqueda | `GET /search/suggest`, `GET /search/semantic` |
| Referencia | `GET /categories`, `/countries`, `/ingredients`, `/microbes`, `/references`, `/diets`, `/seasonal`, `/glossary` |
| Ingredientes | `GET /ingredients/{id}/nutrition`, `/shelf-life` |
| Herramientas | `GET /recommendations`, `/timers/{id}`, `/flavor-map`, `/timeline` |
| Contenido | `GET /guides`, `/guides/{slug}`, `/course`, `/course/{slug}`, `/podcast`, `/podcast/topics`, `/etymology/search` |
| Estadísticas | `GET /stats` |

### API pública versionada

Todo el catálogo también se expone bajo `/api/v1/...` (mismo contrato), con landing en `/api` y healthcheck en `/api/health`. Límite: 120 peticiones/minuto por IP.

```bash
curl "http://localhost:8000/api/v1/products?q=kimchi&page_size=3"
```

### Servidor MCP

`mcp_server/` expone el catálogo a asistentes de IA (Claude Desktop y compatibles) con herramientas de búsqueda, detalle, recomendaciones y temporizadores.

## Fuentes de datos y licencias

| Fuente | Contenido | Licencia |
|---|---|---|
| FermDB (ETH Zurich) | Fermentos tradicionales del mundo | CC BY 4.0 |
| Wikipedia (7 listas: fermentados, encurtidos, lácteos, leche fermentada, quesos, soja) | Entradas adicionales e imágenes | CC BY-SA 4.0 |
| Open Food Facts (35+ categorías) | Productos comerciales, con tope por categoría | ODbL |
| Wikidata | Enriquecimiento (label, descripción, país) | CC0 |
| Slow Food Ark of Taste | Productos patrimoniales | CC BY-SA 4.0 |
| FDF-DB / MetaCheeseDB | Lácteos fermentados y metagenomas de quesos | Académico |
| USDA FoodKeeper | Guías de vida útil (adaptadas) | Dominio público |

### Estado del catálogo

**6.182 productos** (5.935 activos + 247 descartados por curaduría), **147 países**, 203 ingredientes canónicos, 41 microbios, 3.269 referencias, ~4.900 vínculos de uso entre productos, 1.264 lácteos fermentados y 267 metagenomas de quesos.

Cobertura: 99,98% de productos con ≥1 ingrediente, ~99% con sustrato principal identificado, imágenes para ~57% del catálogo (pipeline Wikimedia en curso).

Distribución por categoría (16/16 activas): fermento_láctico 1.387, encurtido_fermentado 960, conserva_esterilizada 866, fermento_alcohólico 542, fermento_koji 519, conserva_azúcar 449, encurtido_vinagre 372, fermento_acético 221, encurtido_salmuera 155, ahumado 141, conserva_aceite 138, secado 117, curado_sal 68, fermento_mixto 44, fermento_alcalino 5.

### Curaduría

`uv run python -m ingest.curation --apply` fusiona variantes del mismo producto (~100+ grupos curados a mano), capitaliza nombres y descarta ruido. La API ignora los descartados; reporte de pares similares pendientes con `--report`.

Las descargas remotas se cachean en `data/raw/` respetando rate-limits con reintentos y backoff. La búsqueda usa FTS5 y cae a subcadena si no está disponible.

## Desarrollo

- **Tests**: `uv run pytest` — 322 tests (API, servicios, frontend servido, ingesta)
- **Lint**: `ruff check .` · **Tipos**: `mypy app`
- **CI**: GitHub Actions corre pytest + ruff + mypy en cada push a `main`

## Despliegue

`render.yaml` incluido para Render (región Frankfurt, plan free):

```bash
# build: pip install uv && uv sync
# start: uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Licencia

Código bajo MIT (ver `LICENSE`). Los datos agregados provienen de fuentes abiertas que requieren atribución: FermDB (CC BY 4.0), Wikipedia (CC BY-SA 4.0), Open Food Facts (ODbL), Wikidata (CC0), Ark of Taste (CC BY-SA 4.0). La base compilada (`data/build.db`) no se distribuye; se genera con `uv run python -m ingest.ingest`.
