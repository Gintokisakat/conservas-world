# Conservas del Mundo

Base de datos mundial de conservas, fermentos y encurtidos tradicionales.

## Stack

- **Backend**: Python + FastAPI + SQLAlchemy
- **BD**: SQLite (FTS5 para búsqueda), migrable a PostgreSQL
- **Ingesta**: Pipeline automático desde fuentes abiertas (FermDB, Wikipedia)

## Estructura

```
app/       → API FastAPI + modelos SQLAlchemy
ingest/    → pipeline de ingesta y normalización
data/      → descargas raw, datos de referencia, build.db
tests/     → tests pytest
```

## Comandos

```bash
uv sync                       # instalar dependencias
uv run python -m ingest.ingest             # construir la base de datos (data/build.db)
uv run python -m ingest.ingest --reset     # reconstruirla desde cero
uv run uvicorn app.main:app --reload       # servir la API en http://localhost:8000
uv run pytest                 # ejecutar tests
```

Si `uv` no se encuentra: `export PATH="$HOME/.local/bin:$PATH"`.

Docs de la API en http://localhost:8000/docs

## Web app

La interfaz web (HTML/CSS/JS sin dependencias de frontend) se sirve en la raíz:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# Abrir http://localhost:8000
```

Permite buscar, filtrar por categoría/continente/país/fuente, ver detalles (ingredientes, microbios, referencias) y un producto aleatorio. Incluye un panel "Mi despensa": cargás qué ingredientes y fermentados tenés, y te recomienda qué podés *hacer* (por sustrato disponible) y qué podés *usar* (fermentados que consumen lo que ya tenés). La despensa se guarda en tu navegador (localStorage).

## API

| Endpoint | Descripción |
|---|---|
| `GET /products` | Lista paginada con filtros `q`, `category`, `country`, `continent`, `ingredient`, `source`, `status`, `page`, `page_size` |
| `GET /products/{id}` | Detalle completo (alias, países, ingredientes, categorías, microbios, referencias, sustrato y usos) |
| `GET /products/random` | Producto aleatorio |
| `GET /products/{id}/related` | Productos relacionados por categoría compartida |
| `GET /recommendations` | Recomendaciones con `ingredients` (sustratos que tenés) y `products` (fermentados que tenés): devuelve `make` (qué podés hacer) y `use` (qué podés preparar con lo fermentado) |
| `GET /categories` | Taxonomía de categorías |
| `GET /countries` | Países (filtrable por `continent`) |
| `GET /ingredients` | Ingredientes canónicos |
| `GET /references` | Referencias |
| `GET /stats` | Estadísticas globales (incluye cobertura de ingredientes y vínculos de uso) |

## Fuentes de datos y licencias

| Fuente | Contenido | Licencia |
|---|---|---|
| FermDB (ETH Zurich) | Fermentos tradicionales del mundo | CC BY 4.0 |
| Wikipedia (7 listas: fermentados, encurtidos, lácteos, leche fermentada, quesos, soja) | Entries adicionales | CC BY-SA 4.0 |
| Open Food Facts (16 categorías de fermentados, encurtidos y conservas) | Productos comerciales, con tope por categoría | ODbL |
| Wikidata (categorías EN + ES de fermentados, encurtidos y bebidas) | Enriquecido con label, descripción y país de origen | CC0 |

Estado actual del seed: **2895 productos** (2784 activos + 111 descartados por curaduría: FermDB 605, Wikipedia 715, Open Food Facts 1590, Wikidata 89), 133 países, ~2400 referencias.

Cobertura de datos: **86% de los productos con ≥1 ingrediente** (193 ingredientes canónicos, normalizados con vocabulario EN + aliases ES/FR, tipografías corregidas), **82% con sustrato principal** identificado (lo que fermentás: repollo, leche, soja…) y **~1900 vínculos de uso** entre productos (qué fermentado usa qué otro como ingrediente).

Distribución de categorías: fermento_lactico 1335, encurtido_fermentado 516, fermento_koji 383, fermento_alcoholico 291, conserva_azucar 309 (mermeladas, frutas confitadas), encurtido_vinagre 138 (pepinillos, alcaparras, escabeches), fermento_acetico 140, otros ~55.

### Curaduría

`uv run python -m ingest.curation --apply` limpia la base: fusiona variantes del mismo producto (alias + absorción de datos, marcando los duplicados como `discarded`), capitaliza nombres, y descarta ruido (p.ej. aceite de hígado de bacalao). Incluye ~65 grupos curados a mano (`CURATED_MERGES`: grafías y lenguas distintas tipo *Choucroute cuisinée*/*La Choucroute cuisinée*, *Miso Paste dunkel*/*Misopaste dunkel*) y fusión automática de variantes OFF (mismas marcas con diferencias de formato). La API y la ingesta ignoran los productos descartados; el reporte de pares similares pendientes se genera con `--report`.

El código se publica bajo licencia MIT (ver `LICENSE`). Los datos agregados provienen de fuentes abiertas que requieren atribución: FermDB (CC BY 4.0), Wikipedia (CC BY-SA 4.0), Open Food Facts (ODbL) y Wikidata (CC0). La base de datos compilada (`data/build.db`) no se distribuye en el repositorio; se genera con `uv run python -m ingest.ingest`.

La búsqueda (`q`) usa FTS5 cuando la tabla está disponible y cae a búsqueda por subcadena en caso contrario.

Las descargas remotas se cachean en `data/raw/` (Wikipedia, Wikidata y Open Food Facts por página/consulta), respetando rate-limits con reintentos y backoff.
