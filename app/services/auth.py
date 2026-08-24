"""Autenticación de usuarios (roadmap 4.1).

- Hash de contraseñas con scrypt (stdlib, sin dependencias nativas).
- Tokens JWT: acceso (30 min) + refresco (30 días) con PyJWT.
- Rate limit propio por endpoint para registro y login.
"""

import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

import jwt

ACCESS_TOKEN_MINUTES = 30
REFRESH_TOKEN_DAYS = 30
_MIN_PASSWORD_LEN = 8

_SECRET_FILE = Path(os.environ.get("CONSERVAS_DATA_DIR", "data")) / ".jwt_secret"


def get_secret() -> str:
    env = os.environ.get("CONSERVAS_JWT_SECRET")
    if env:
        return env
    _SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    if _SECRET_FILE.exists() and len(_SECRET_FILE.read_text().strip()) >= 32:
        return _SECRET_FILE.read_text().strip()
    secret = secrets.token_urlsafe(48)
    _SECRET_FILE.write_text(secret)
    return secret


# --- Contraseñas -----------------------------------------------------------

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n, r, p, salt_hex, digest_hex = stored.split("$")
        if scheme != "scrypt":
            return False
        digest = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p), dklen=32
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False


# --- Tokens ----------------------------------------------------------------

def _encode(payload: dict, minutes: int) -> str:
    body = {**payload, "iat": int(time.time()), "exp": int(time.time()) + minutes * 60}
    return jwt.encode(body, get_secret(), algorithm="HS256")


def create_access_token(user_id: int) -> str:
    return _encode({"sub": str(user_id), "type": "access"}, ACCESS_TOKEN_MINUTES)


def create_refresh_token(user_id: int) -> str:
    return _encode({"sub": str(user_id), "type": "refresh"}, REFRESH_TOKEN_DAYS * 24 * 60)


def decode_token(token: str, expected_type: str = "access") -> int | None:
    """Devuelve el user_id si el token es válido del tipo esperado; si no None."""
    try:
        payload = jwt.decode(token, get_secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    try:
        return int(payload["sub"])
    except (KeyError, ValueError):
        return None


# --- Rate limit por endpoint ----------------------------------------------

_AUTH_LIMIT = 10
_AUTH_WINDOW = 60.0
_attempts: dict[str, list[float]] = {}


def check_auth_rate(key: str) -> bool:
    """True si la acción está permitida para la clave (ip:endpoint)."""
    now = time.monotonic()
    window = [t for t in _attempts.get(key, []) if now - t < _AUTH_WINDOW]
    if len(window) >= _AUTH_LIMIT:
        _attempts[key] = window
        return False
    window.append(now)
    _attempts[key] = window
    return True


# --- Preferencias ----------------------------------------------------------

def parse_preferences(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}
