from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.public import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, check_rate_limit
from app.api.public import router as public_router
from app.api.routes import router
from app.api.seo import router as seo_router
from app.db.database import engine as _engine

STATIC_DIR = Path(__file__).resolve().parent / "static"


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
    app.include_router(public_router)
    app.include_router(seo_router)

    # Las tablas de usuario no vienen en el snapshot de la BD: se crean
    # de forma idempotente al arrancar (roadmap 4.1).
    try:
        from sqlalchemy import Table as _SaTable

        from app.db import models as _models

        for table in (_models.User.__table__, _models.Review.__table__, _models.Recipe.__table__):
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
