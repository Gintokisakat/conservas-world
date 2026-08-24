"""Calentamiento de cachés al arrancar el proceso.

En hosting con CPU limitada (p. ej. Render free), la primera petición a
búsquedas semánticas, mapa de sabores o estadísticas pagaba la construcción
de índices (~5-10 s). Este módulo precarga todo en un hilo de fondo justo
tras el arranque, de modo que los visitantes lleguen a cachés calientes.
"""

import threading

from app.db.database import SessionLocal

_done = threading.Event()


def run_warmup() -> list[str]:
    """Precarga los cachés pesados. Devuelve los pasos que fallaron."""
    errors: list[str] = []

    session = SessionLocal()
    try:
        from app.services.semantic import _build_index

        _build_index(session)
    except Exception:
        errors.append("semantic")
    finally:
        session.close()

    session = SessionLocal()
    try:
        from app.services.flavors import flavor_map_payload

        flavor_map_payload(session, detail=False)
        flavor_map_payload(session, detail=True)
    except Exception:
        errors.append("flavor-map")
    finally:
        session.close()

    try:
        from app.services.stats_service import warm_stats

        warm_stats()
    except Exception:
        errors.append("stats")

    if not errors:
        _done.set()
    return errors


def start_background_warmup() -> threading.Thread | None:
    """Lanza el calentamiento en un hilo daemon (una sola vez por proceso)."""
    import os

    if os.environ.get("CONSERVAS_WARMUP", "1") != "1":
        return None
    if _done.is_set():
        return None

    def _job() -> None:
        try:
            run_warmup()
        except Exception:
            pass

    thread = threading.Thread(target=_job, name="warmup", daemon=True)
    thread.start()
    return thread