"""Seguimiento de fermentos/frascos del usuario (roadmap 3.1)."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db import models
from app.db.database import get_session
from app.schemas import BatchCreate, BatchesOut, BatchOut, BatchUpdate

router = APIRouter(tags=["batches"])


def _batch_out(batch: models.Batch) -> BatchOut:
    return BatchOut(
        id=batch.id,
        name=batch.name,
        substrate=batch.substrate,
        method=batch.method,
        start_date=batch.start_date,
        target_days=batch.target_days,
        temp_c=batch.temp_c,
        ph=batch.ph,
        notes=batch.notes,
        status=batch.status,
        created_at=batch.created_at,
        updated_at=batch.updated_at,
    )


def _load_mine(session: Session, batch_id: int, user: models.User) -> models.Batch:
    batch = session.get(models.Batch, batch_id)
    if batch is None or batch.user_id != user.id:
        raise HTTPException(status_code=404, detail="Fermento no encontrado")
    return batch


def _apply_updates(batch: models.Batch, body: BatchUpdate | Any) -> None:
    if body.name is not None:
        batch.name = body.name.strip() or batch.name
    if body.substrate is not None:
        batch.substrate = body.substrate
    if body.method is not None:
        batch.method = body.method
    if body.start_date is not None:
        batch.start_date = body.start_date
    if body.target_days is not None:
        batch.target_days = body.target_days
    if body.temp_c is not None:
        batch.temp_c = body.temp_c
    if body.ph is not None:
        batch.ph = body.ph
    if body.notes is not None:
        batch.notes = body.notes
    if body.status is not None:
        batch.status = body.status


@router.get("/me/batches", response_model=BatchesOut)
def list_batches(
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.execute(
        select(models.Batch)
        .where(models.Batch.user_id == user.id)
        .order_by(models.Batch.created_at.desc())
    ).scalars().all()
    return BatchesOut(total=len(rows), items=[_batch_out(r) for r in rows])


@router.post("/me/batches", response_model=BatchOut, status_code=201)
def create_batch(
    body: BatchCreate,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    batch = models.Batch(
        user_id=user.id,
        name=body.name.strip(),
        substrate=body.substrate,
        method=body.method,
        start_date=body.start_date or models.func.now(),
        target_days=body.target_days,
        temp_c=body.temp_c,
        ph=body.ph,
        notes=body.notes,
        status=body.status,
    )
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return _batch_out(batch)


@router.put("/me/batches/{batch_id}", response_model=BatchOut)
def update_batch(
    batch_id: int,
    body: BatchUpdate,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    batch = _load_mine(session, batch_id, user)
    _apply_updates(batch, body)
    session.commit()
    session.refresh(batch)
    return _batch_out(batch)


@router.delete("/me/batches/{batch_id}", status_code=204)
def delete_batch(
    batch_id: int,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    batch = _load_mine(session, batch_id, user)
    session.delete(batch)
    session.commit()