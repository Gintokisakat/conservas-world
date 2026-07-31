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

Permite buscar, filtrar por categoría/continente/país/fuente, ver detalles (ingredientes, microbios, referencias) y un producto aleatorio.

## API

| Endpoint | Descripción |
|---|---|
| `GET /products` | Lista paginada con filtros `q`, `category`, `country`, `continent`, `ingredient`, `source`, `status`, `page`, `page_size` |
| `GET /products/{id}` | Detalle completo (alias, países, ingredientes, categorías, microbios, referencias) |
| `GET /products/random` | Producto aleatorio |
| `GET /products/{id}/related` | Productos relacionados por categoría compartida |
| `GET /categories` | Taxonomía de categorías |
| `GET /countries` | Países (filtrable por `continent`) |
| `GET /ingredients` | Ingredientes |
| `GET /references` | Referencias |
| `GET /stats` | Estadísticas globales |

## Fuentes de datos y licencias

| Fuente | Contenido | Licencia |
|---|---|---|
| FermDB (ETH Zurich) | Fermentos tradicionales del mundo | CC BY 4.0 |
| Wikipedia (7 listas: fermentados, encurtidos, lácteos, leche fermentada, quesos, soja) | Entries adicionales | CC BY-SA 4.0 |
| Open Food Facts (11 categorías de fermentados/encurtidos) | Productos comerciales, con tope por categoría | ODbL |
| Wikidata (categorías EN + ES de fermentados, encurtidos y bebidas) | Enriquecido con label, descripción y país de origen | CC0 |

Estado actual del seed: **2554 productos** (FermDB 605, Wikipedia 715, Open Food Facts 1145, Wikidata 89), 133 países, ~490 ingredientes, ~20 microbios, ~2400 referencias.

Distribución de categorías: fermento_lactico 1335, encurtido_fermentado 497, fermento_koji 383, fermento_alcoholico 290, fermento_acetico 140, otros ~55.

El código se publica bajo licencia MIT (ver `LICENSE`). Los datos agregados provienen de fuentes abiertas que requieren atribución: FermDB (CC BY 4.0), Wikipedia (CC BY-SA 4.0), Open Food Facts (ODbL) y Wikidata (CC0). La base de datos compilada (`data/build.db`) no se distribuye en el repositorio; se genera con `uv run python -m ingest.ingest`.

La búsqueda (`q`) usa FTS5 cuando la tabla está disponible y cae a búsqueda por subcadena en caso contrario.

Las descargas remotas se cachean en `data/raw/` (Wikipedia, Wikidata y Open Food Facts por página/consulta), respetando rate-limits con reintentos y backoff.
