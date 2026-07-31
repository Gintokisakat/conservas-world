# Conservas del Mundo - Guía de Desarrollo para Agentes AI (GEMINI.md)

## 📌 Información del Proyecto
- **Nombre**: Conservas del Mundo
- **Ruta Absoluta del Proyecto**: `/home/epil/Proyectos/conservas-world`
- **Descripción**: Base de datos mundial y aplicación web interactiva de conservas, fermentos y encurtidos tradicionales.

## 🏗 Arquitectura y Tecnologías
- **Backend**: Python (>=3.11) + FastAPI + SQLAlchemy + SQLite (con búsqueda FTS5 `products_fts`).
- **Frontend**: HTML5 + CSS3 (Vanilla) + Javascript (Vanilla) ubicado en `app/static/`.
- **Gestor de paquetes / entorno**: `uv`
- **Pipeline de Ingesta**: `ingest/` (procesa FermDB, Wikipedia, Open Food Facts y Wikidata).

## 🚀 Comandos Frecuentes
```bash
# Instalar dependencias
uv sync

# Ejecutar el servidor de desarrollo
uv run uvicorn app.main:app --reload --port 8000

# Ejecutar las pruebas unitarias
uv run pytest

# Reconstruir la base de datos de ingesta desde cero
uv run python -m ingest.ingest --reset

# Aplicar reglas de curaduría a la base de datos
uv run python -m ingest.curation --apply
```

## 📁 Estructura del Código
- `app/`
  - `main.py` -> Punto de entrada FastAPI y montaje de archivos estáticos.
  - `api/routes.py` -> Endpoints REST (`/products`, `/recommendations`, `/categories`, etc.).
  - `db/` -> `database.py` (conexión SQLAlchemy) y `models.py` (modelos de datos).
  - `schemas.py` -> Modelos Pydantic para request/response.
  - `static/` -> Frontend web (`index.html`, `style.css`, `app.js`).
- `ingest/` -> Scripts de normalización, etiquetado de sustratos, curaduría e ingesta.
- `data/` -> Base de datos SQLite compilada (`build.db`) y archivos raw.
- `tests/` -> Pruebas de integración y unitarias con `pytest`.
