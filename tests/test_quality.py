"""Tests de calidad (5.5): warmup y helpers de la base de datos."""

import threading

from app.services import warmup


def test_run_warmup_returns_error_list():
    errors = warmup.run_warmup()
    # Con la DB real, todo el warmup debería completarse sin errores
    assert errors == []
    assert warmup._done.is_set()


def test_run_warmup_is_reentrant():
    # Ejecutar de nuevo no debe lanzar excepciones
    assert warmup.run_warmup() == []


def test_start_background_warmup_respects_env(monkeypatch):
    # CONSERVAS_WARMUP=0 en tests => no lanza hilo
    warmup._done.clear()
    monkeypatch.setenv("CONSERVAS_WARMUP", "0")
    assert warmup.start_background_warmup() is None


def test_start_background_warmup_returns_thread():
    warmup._done.clear()
    monkeypatch_warmup = _patch_enable()
    try:
        thread = warmup.start_background_warmup()
        assert isinstance(thread, threading.Thread)
        assert thread.daemon
        thread.join(10)
    finally:
        monkeypatch_warmup()


def _patch_enable():
    import os

    os.environ.pop("CONSERVAS_WARMUP", None)
    return lambda: os.environ.setdefault("CONSERVAS_WARMUP", "0")