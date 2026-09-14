import logging
import uuid
from pathlib import Path
from time import monotonic

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.batches import router as batches_router
from app.api.breweries import router as breweries_router
from app.api.producers import router as producers_router
from app.api.public import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, check_rate_limit, record_request
from app.api.public import router as public_router
from app.api.recipes import router as recipes_router
from app.api.reviews import router as reviews_router
from app.api.routes import router
from app.api.seo import router as seo_router
from app.db.database import engine as _engine

_access_logger = logging.getLogger("conservas.access")

STATIC_DIR = Path(__file__).resolve().parent / "static"

# Roadmap 5.3 — cabeceras de caché para endpoints de lectura. Las reglas más
# específicas van primero; el middleware respeta el Cache-Control que los
# endpoints ya fijen y solo rellena el resto.
_CACHE_RULES: list[tuple[str, str]] = [
    ("/products/random", "no-store"),
    ("/search/", "public, max-age=60"),
    ("/api/v1/me", "private, no-store"),
    ("/me", "private, no-store"),
    ("/auth", "private, no-store"),
    ("/stats", "public, max-age=300"),
    ("/seasonal", "public, max-age=86400"),
    ("/timeline", "public, max-age=86400"),
    ("/guides", "public, max-age=86400"),
    ("/glossary", "public, max-age=86400"),
    ("/course", "public, max-age=86400"),
    ("/podcast", "public, max-age=86400"),
    ("/etymology", "public, max-age=86400"),
    ("/flavor-map", "public, max-age=86400"),
    ("/categories", "public, max-age=3600"),
    ("/countries", "public, max-age=3600"),
    ("/ingredients", "public, max-age=3600"),
    ("/diets", "public, max-age=3600"),
    ("/microbes", "public, max-age=3600"),
    ("/references", "public, max-age=3600"),
    ("/products", "public, max-age=3600"),
]

_DEFAULT_CACHE = "public, max-age=300"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Conservas del Mundo",
        description="Base de datos mundial de conservas, fermentos y encurtidos",
        version="0.2.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.include_router(router, prefix="/api/v1")
    app.include_router(auth_router)
    app.include_router(reviews_router)
    app.include_router(reviews_router, prefix="/api/v1")
    app.include_router(recipes_router)
    app.include_router(recipes_router, prefix="/api/v1")
    app.include_router(batches_router)
    app.include_router(batches_router, prefix="/api/v1")
    app.include_router(producers_router)
    app.include_router(producers_router, prefix="/api/v1")
    app.include_router(breweries_router)
    app.include_router(breweries_router, prefix="/api/v1")
    app.include_router(public_router)
    app.include_router(seo_router)

    # Las tablas de usuario no vienen en el snapshot de la BD: se crean
    # de forma idempotente al arrancar (roadmap 4.1).
    try:
        from sqlalchemy import Table as _SaTable

        from app.db import models as _models

        for table in (
            _models.User.__table__,
            _models.Review.__table__,
            _models.Recipe.__table__,
            _models.RecipeVote.__table__,
            _models.FlavorMolecule.__table__,
            _models.IngredientFlavorMolecule.__table__,
            _models.Batch.__table__,
            _models.BatchCheckpoint.__table__,
            _models.Producer.__table__,
            _models.Brewery.__table__,
            _models.SourceVersion.__table__,
        ):
            assert isinstance(table, _SaTable)
            table.create(bind=_engine, checkfirst=True)
    except Exception:
        pass


    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.middleware("http")
    async def rate_limit_middleware(request, call_next):
        if request.url.path.startswith("/api"):
            client_key = request.client.host if request.client else "unknown"
            remaining = check_rate_limit(client_key)
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(RATE_LIMIT_WINDOW))
            return response
        return await call_next(request)

    @app.middleware("http")
    async def cache_control_middleware(request, call_next):
        response = await call_next(request)
        if request.method in ("GET", "HEAD") and "Cache-Control" not in response.headers:
            path = request.url.path
            if path in ("/", ""):
                # El shell del SPA es pequeño pero cambia con cada deploy;
                # mejor revalidarlo siempre para no servir un app.js viejo.
                response.headers["Cache-Control"] = "no-cache"
                return response
            # Las reglas viven sin el prefijo de API; las rutas duplicadas
            # (/products y /api/v1/products) deben recibir el mismo cabecero.
            base = path.removeprefix("/api/v1")
            for prefix, directive in _CACHE_RULES:
                if base.startswith(prefix):
                    response.headers["Cache-Control"] = directive
                    break
            else:
                response.headers["Cache-Control"] = _DEFAULT_CACHE
        return response

    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        """Roadmap 5.4 — logs de acceso con Request-ID y métricas para /api/health."""
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id
        start = monotonic()
        response = await call_next(request)
        msec = (monotonic() - start) * 1000.0
        response.headers["X-Request-ID"] = req_id
        if request.url.path.startswith("/api"):
            record_request(
                request.url.path.removesuffix("/")
                or "/",
                msec,
            )
        _access_logger.info(
            "[%s] %s %s -> %s (%.1f ms)",
            req_id,
            request.method,
            request.url.path,
            response.status_code,
            msec,
        )
        return response


    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    return app


app = create_app()


def _start_warmup() -> None:
    try:
        from app.services.warmup import start_background_warmup

        start_background_warmup()
    except Exception:
        pass


_start_warmup()
