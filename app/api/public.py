import logging
import time
from collections import defaultdict, deque
from time import monotonic

from fastapi import APIRouter
from sqlalchemy import text

from app.api.routes import router as api_router
from app.db.database import engine

logger = logging.getLogger("conservas")

router = APIRouter(prefix="/api")

RATE_LIMIT_REQUESTS = 120
RATE_LIMIT_WINDOW = 60.0

_request_log: defaultdict[str, deque[float]] = defaultdict(deque)

# Roadmap 5.4 — monitoreo: uptime y estadísticas por ruta.
_START_TS = time.time()
_SAMPLE_LIMIT = 200
_by_path: defaultdict[str, deque[float]] = defaultdict(lambda: deque(maxlen=_SAMPLE_LIMIT))


def check_rate_limit(client_key: str) -> int:
    now = monotonic()
    window = _request_log[client_key]
    while window and now - window[0] > RATE_LIMIT_WINDOW:
        window.popleft()
    window.append(now)
    return max(0, RATE_LIMIT_REQUESTS - len(window))


def record_request(path: str, msec: float) -> None:
    """Acumula una muestra de latencia para una ruta (monitoreo 5.4)."""
    _by_path[path].append(msec)


def reset_monitoring() -> None:
    _by_path.clear()


def _quantile(samples: deque[float], q: float) -> float | None:
    if not samples:
        return None
    ordered = sorted(samples)
    return ordered[min(len(ordered) - 1, int(len(ordered) * q))]


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
    """Estado del servicio: base de datos, uptime y métricas agregadas."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            try:
                conn.execute(text("SELECT 1 FROM products LIMIT 1"))
                db_status = "ok"
            except Exception:
                db_status = "empty"
        service = "ok"
    except Exception:
        db_status = "error"
        service = "degraded"

    rows = []
    total = 0
    ranked = sorted(
        (
            (
                path,
                len(samples),
                round(_quantile(samples, 0.95) or 0.0, 1),
                round(sum(samples) / len(samples), 1),
            )
            for path, samples in _by_path.items()
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    for path, count, p95, avg in ranked:
        total += count
        rows.append({"path": path, "count": count, "p95_ms": p95, "avg_ms": avg})

    return {
        "status": service,
        "db": db_status,
        "version": "0.2.0",
        "uptime_seconds": int(time.time() - _START_TS),
        "requests_total": total,
        "requests_by_path": rows[:20],
    }