"""Endpoints de autenticación (roadmap 4.1)."""

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models
from app.db.database import get_session
from app.schemas import (
    PreferencesUpdate,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserLogin,
    UserOut,
)
from app.services.auth import (
    check_auth_rate,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    parse_preferences,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_key(request: Request, action: str) -> str:
    ip = request.client.host if request.client else "unknown"
    return f"{ip}:{action}"


def _token_pair(user_id: int) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


def _user_out(user: models.User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at,
        preferences=parse_preferences(user.preferences_json),
    )


@router.post("/register", response_model=TokenPair, status_code=201)
def register(
    request: Request,
    body: UserCreate,
    session: Session = Depends(get_session),
):
    if not check_auth_rate(_client_key(request, "register")):
        raise HTTPException(status_code=429, detail="Demasiados intentos; espera un minuto")
    email = body.email.lower().strip()
    existing = session.execute(
        select(models.User).where(
            (models.User.email == email) | (models.User.username == body.username.lower())
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email o usuario ya registrado")
    user = models.User(
        email=email,
        username=body.username.lower(),
        password_hash=hash_password(body.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return _token_pair(user.id)


@router.post("/login", response_model=TokenPair)
def login(
    request: Request,
    body: UserLogin,
    session: Session = Depends(get_session),
):
    if not check_auth_rate(_client_key(request, "login")):
        raise HTTPException(status_code=429, detail="Demasiados intentos; espera un minuto")
    user = session.execute(
        select(models.User).where(models.User.email == body.email.lower().strip())
    ).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return _token_pair(user.id)


@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshRequest):
    user_id = decode_token(body.refresh_token, expected_type="refresh")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
    return _token_pair(user_id)


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> models.User:
    """Resuelve el usuario desde el header `Authorization: Bearer <token>`."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta el token de acceso")
    user_id = decode_token(authorization[7:].strip())
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    user = session.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


@router.get("/me", response_model=UserOut)
def me(user: models.User = Depends(get_current_user)):
    return _user_out(user)


@router.put("/me/preferences", response_model=UserOut)
def update_preferences(
    body: PreferencesUpdate,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    import json

    user.preferences_json = json.dumps(body.preferences, ensure_ascii=False)
    session.add(user)
    session.commit()
    session.refresh(user)
    return _user_out(user)
