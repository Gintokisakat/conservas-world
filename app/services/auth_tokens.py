"""Tokens opacos para verificación y reset (one-time)."""

import hashlib
import os
from datetime import datetime, timedelta


def _token_bytes() -> bytes:
    return os.urandom(32)


def generate_token() -> tuple[str, str]:
    t = _token_bytes().hex()
    h = hashlib.sha256(t.encode()).hexdigest()
    return t, h


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def expires_in(hours: int = 1) -> datetime:
    return datetime.utcnow() + timedelta(hours=hours)
