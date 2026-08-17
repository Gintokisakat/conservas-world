from collections import defaultdict, deque
from time import monotonic

from fastapi import APIRouter
from sqlalchemy import text

from app.api.routes import router as api_router
from app.db.database import engine

router = APIRouter(prefix="/api")

RATE_LIMIT_REQUESTS = 120
RATE_LIMIT_WINDOW = 60.0

_requests: defaultdict[str, deque[float]] = defaultdict(deque)


def check_rate_limit(client_key: str) -> int:
    now = monotonic()
    window = _requests[client_key]
    while window and now - window[0] > RATE_LIMIT_WINDOW:
        window.popleft()
    window.append(now)
    return max(0, RATE_LIMIT_REQUESTS - len(window))


@router.get("", response_model=None)
@router.get("/", response_model=None)
def api_root() -> dict:
    """Raíz de la API pública: versionado, documentación y listado de endpoints."""
    endpoints = []
    for route in api_router.routes:
        path = getattr(route, "path", "")
        if path in ("/", ""):
            continue
        for method in getattr(route, "methods", set()) - {"HEAD", "OPTIONS"}:
            endpoints.append(
                {
                    "method": method,
                    "path": f"/api/v1{path}",
                    "name": getattr(route, "name", None),
                    "summary": (getattr(route, "summary", None) or "")[:200] or None,
                }
            )
    return {
        "name": "Conservas del Mundo API",
        "version": "v1",
        "base_url": "/api/v1",
        "documentation": "/docs",
        "rate_limit": {
            "requests": RATE_LIMIT_REQUESTS,
            "window_seconds": RATE_LIMIT_WINDOW,
            "headers": ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
        },
        "endpoints": sorted(endpoints, key=lambda e: (e["method"], e["path"])),
    }


@router.get("/health", response_model=None)
def api_health() -> dict:
    """Estado del servicio y de la base de datos."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status}