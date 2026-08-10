# Conservas del Mundo

Base de datos mundial de conservas, fermentos y encurtidos tradicionales.

## Stack

- **Backend**: Python + FastAPI + SQLAlchemy
- **BD**: SQLite (FTS5 para búsqueda), migrable a PostgreSQL
- **Ingesta**: Pipeline automático desde fuentes abiertas (FermDB, Wikipedia, Open Food Facts, Wikidata)
- **Frontend**: HTML/CSS/JS vanilla con i18n (ES/EN), Chart.js, PWA

## Estructura

```
app/       → API FastAPI + modelos SQLAlchemy + frontend
ingest/    → pipeline de ingesta y normalización
data/      → descargas raw, datos de referencia, build.db
tests/     → tests pytest (74 tests)
```

## Comandos

```bash
uv sync                       # instalar dependencias
uv run python -m ingest.ingest             # construir la base de datos (data/build.db)
uv run python -m ingest.ingest --reset     # reconstruirla desde cero
uv run uvicorn app.main:app --reload       # servir la API en http://localhost:8000
uv run pytest                 # ejecutar tests (74 tests)
```

Si `uv` no se encuentra: `export PATH="$HOME/.local/bin:$PATH"`.

Docs de la API en http://localhost:8000/docs

## Web app

La interfaz web (HTML/CSS/JS sin dependencias de frontend) se sirve en la raíz:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# Abrir http://localhost:8000
```

### Features

- **Búsqueda y filtros**: buscar por nombre/descripción, filtrar por categoría, continente, país, fuente
- **Detalle de producto**: alias, países, ingredientes, categorías, microbios, referencias, sustrato y usos
- **Producto aleatorio**: botón "Sorpréndeme"
- **Mi Despensa Interactiva**: cargás qué ingredientes y fermentados tenés, y te recomienda qué podés *hacer* (por sustrato disponible) y qué podés *usar* (fermentados que consumen lo que ya tenés). La despensa se guarda en tu navegador (localStorage)
- **Temporizador de fermentos**: monitoreo de frascos en F1/F2 con barra de progreso
- **Calculadora de salinidad**: gramos de sal para fermentación láctica segura
- **Calculadora de ABV**: estimación de alcohol para hidromiel, sidra, kvas o cerveza
- **Diagnóstico de problemas**: guía visual de troubleshoot (kahm, moho, salmuera turbia, olor fétido, vegetales blandos)
- **Enciclopedia de microbios**: lista de bacterias, hongos y levaduras con búsqueda
- **Etiquetas imprimibles**: generación de etiquetas para frascos
- **Panel de estadísticas**: gráficos de distribución por continente, fuente y categoría (Chart.js)
- **Manual del fermentador**: guía científica de esterilización, salinidad, textura y control de oxígeno
- **Favoritos**: marcador de productos guardados
- **Lista de compras**: ingredientes faltantes para las recetas recomendadas
- **i18n**: interfaz bilingüe español/inglés
- **PWA**: service worker para soporte offline

## API

| Endpoint | Descripción |
|---|---|
| `GET /products` | Lista paginada con filtros `q`, `category`, `country`, `continent`, `ingredient`, `source`, `status`, `page`, `page_size` |
| `GET /products/{id}` | Detalle completo (alias, países, ingredientes, categorías, microbios, referencias, sustrato y usos). Soporta `lang=en` para alias en inglés |
| `GET /products/random` | Producto aleatorio |
| `GET /products/{id}/related` | Productos relacionados por categoría compartida |
| `GET /recommendations` | Recomendaciones con `ingredients` (sustratos que tenés) y `products` (fermentados que tenés): devuelve `make` (qué podés hacer) y `use` (qué podés preparar con lo fermentado) |
| `GET /categories` | Taxonomía de categorías |
| `GET /countries` | Países (filtrable por `continent`) |
| `GET /ingredients` | Ingredientes canónicos |
| `GET /microbes` | Microbios fermentadores |
| `GET /references` | Referencias bibliográficas |
| `GET /stats` | Estadísticas globales (incluye cobertura de ingredientes, vínculos de uso y distribución por categoría/continente/fuente) |

## Fuentes de datos y licencias

| Fuente | Contenido | Licencia |
|---|---|---|
| FermDB (ETH Zurich) | Fermentos tradicionales del mundo | CC BY 4.0 |
| Wikipedia (7 listas: fermentados, encurtidos, lácteos, leche fermentada, quesos, soja) | Entries adicionales | CC BY-SA 4.0 |
| Open Food Facts (35+ categorías de fermentados, encurtidos, cervezas, sakes y conservas) | Productos comerciales, con tope por categoría | ODbL |
| Wikidata (categorías EN + ES de fermentados, encurtidos y bebidas) | Enriquecido con label, descripción y país de origen | CC0 |

### Estado actual del catálogo

**4983 productos** totales (4736 activos + 247 descartados por curaduría), 133 países, ~4900 referencias.

Cobertura de datos: **99.98% de los productos con ≥1 ingrediente** (193 ingredientes canónicos, normalizados con vocabulario EN + aliases ES/FR, tipografías corregidas), **~99% con sustrato principal** identificado (lo que fermentás: repollo, leche, soja…) y **~4900 vínculos de uso** entre productos (qué fermentado usa qué otro como ingrediente).

Distribución de categorías (16/16 con productos): fermento_lactico 1387, encurtido_fermentado 960, conserva_esterilizada 866, fermento_alcoholico 542, fermento_koji 519, conserva_azucar 449, encurtido_vinagre 372, fermento_acetico 221, encurtido_salmuera 155, ahumado 141, conserva_aceite 138, secado 117, curado_sal 68, fermento_mixto 44, fermento_alcalino 5, otros ~28.

### Curaduría

`uv run python -m ingest.curation --apply` limpia la base: fusiona variantes del mismo producto (alias + absorción de datos, marcando los duplicados como `discarded`), capitaliza nombres, y descarta ruido. Incluye ~100+ grupos curados a mano (`CURATED_MERGES`: grafías y lenguas distintas tipo *Choucroute cuisinée*/*La Choucroute cuisinée*, *Miso Paste dunkel*/*Misopaste dunkel*), fusión automática de variantes OFF (mismas marcas con diferencias de formato), y descarte de artefactos Wikipedia y marcas genéricas OFF (`CURATED_DISCARDS`: 22 entradas).

La API y la ingesta ignoran los productos descartados; el reporte de pares similares pendientes se genera con `--report`.

### Despliegue

El proyecto incluye `render.yaml` para despliegue en Render.

El código se publica bajo licencia MIT (ver `LICENSE`). Los datos agregados provienen de fuentes abiertas que requieren atribución: FermDB (CC BY 4.0), Wikipedia (CC BY-SA 4.0), Open Food Facts (ODbL) y Wikidata (CC0). La base de datos compilada (`data/build.db`) no se distribuye en el repositorio; se genera con `uv run python -m ingest.ingest`.

La búsqueda (`q`) usa FTS5 cuando la tabla está disponible y cae a búsqueda por subcadena en caso contrario.

Las descargas remotas se cachean en `data/raw/` (Wikipedia, Wikidata y Open Food Facts por página/consulta), respetando rate-limits con reintentos y backoff.
