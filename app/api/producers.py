"""Networking de productores artesanales (roadmap 4.6)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_user
from app.db import models
from app.db.database import get_session
from app.schemas import (
    ProducerCreate,
    ProducerOut,
    ProducersOut,
    ProducerUpdate,
)

router = APIRouter(tags=["producers"])


def _producer_out(
    producer: models.Producer, user: models.User | None = None
) -> ProducerOut:
    return ProducerOut(
        id=producer.id,
        user_id=producer.user_id,
        name=producer.name,
        country=producer.country,
        region=producer.region,
        city=producer.city,
        address=producer.address,
        latitude=producer.latitude,
        longitude=producer.longitude,
        website=producer.website,
        contact_email=producer.contact_email,
        phone=producer.phone,
        products_offered=producer.products_offered,
        verified=producer.verified,
        created_at=producer.created_at,
        updated_at=producer.updated_at,
        mine=user is not None and producer.user_id == user.id,
    )


@router.get("/producers", response_model=ProducersOut)
def list_producers(
    country: str | None = Query(default=None, description="Filtrar por país"),
    verified: bool | None = Query(default=None, description="Filtrar por verificación"),
    q: str | None = Query(default=None, description="Búsqueda por nombre/ciudad/productos"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: models.User | None = Depends(get_optional_user),
    session: Session = Depends(get_session),
):
    stmt = select(models.Producer)
    if country:
        stmt = stmt.where(func.lower(models.Producer.country) == country.lower().strip())
    if verified is not None:
        stmt = stmt.where(models.Producer.verified == verified)
    if q:
        pattern = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            func.lower(models.Producer.name).like(pattern)
            | func.lower(models.Producer.city).like(pattern)
            | func.lower(models.Producer.region).like(pattern)
            | func.lower(models.Producer.products_offered).like(pattern)
        )

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.scalar(total_stmt) or 0

    stmt = stmt.order_by(models.Producer.verified.desc(), models.Producer.name.asc()).offset(offset).limit(limit)
    producers = session.scalars(stmt).all()

    return ProducersOut(
        total=total,
        items=[_producer_out(p, user) for p in producers],
    )


@router.get("/producers/{producer_id}", response_model=ProducerOut)
def get_producer(
    producer_id: int,
    user: models.User | None = Depends(get_optional_user),
    session: Session = Depends(get_session),
):
    producer = session.get(models.Producer, producer_id)
    if not producer:
        raise HTTPException(status_code=404, detail="Productor no encontrado")
    return _producer_out(producer, user)


@router.post("/producers", response_model=ProducerOut, status_code=201)
def create_producer(
    payload: ProducerCreate,
    user: models.User | None = Depends(get_optional_user),
    session: Session = Depends(get_session),
):
    producer = models.Producer(
        user_id=user.id if user else None,
        name=payload.name.strip(),
        country=payload.country.strip(),
        region=payload.region.strip() if payload.region else None,
        city=payload.city.strip() if payload.city else None,
        address=payload.address.strip() if payload.address else None,
        latitude=payload.latitude,
        longitude=payload.longitude,
        website=payload.website.strip() if payload.website else None,
        contact_email=payload.contact_email.strip() if payload.contact_email else None,
        phone=payload.phone.strip() if payload.phone else None,
        products_offered=payload.products_offered.strip() if payload.products_offered else None,
        verified=False,
    )
    session.add(producer)
    session.commit()
    session.refresh(producer)
    return _producer_out(producer, user)


@router.put("/producers/{producer_id}", response_model=ProducerOut)
def update_producer(
    producer_id: int,
    payload: ProducerUpdate,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    producer = session.get(models.Producer, producer_id)
    if not producer:
        raise HTTPException(status_code=404, detail="Productor no encontrado")
    if producer.user_id is not None and producer.user_id != user.id:
        raise HTTPException(status_code=403, detail="No tenés permiso para editar este productor")

    for field, val in payload.model_dump(exclude_unset=True).items():
        if field == "verified":
            continue  # Solo administradores podrían verificar en el futuro
        if isinstance(val, str):
            val = val.strip()
        setattr(producer, field, val)

    session.commit()
    session.refresh(producer)
    return _producer_out(producer, user)


@router.delete("/producers/{producer_id}")
def delete_producer(
    producer_id: int,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    producer = session.get(models.Producer, producer_id)
    if not producer:
        raise HTTPException(status_code=404, detail="Productor no encontrado")
    if producer.user_id is not None and producer.user_id != user.id:
        raise HTTPException(status_code=403, detail="No tenés permiso para eliminar este productor")

    session.delete(producer)
    session.commit()
    return {"status": "ok", "deleted": producer_id}
