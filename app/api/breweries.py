"""Endpoints para cervecerías/sidrerías (roadmap 2.7) y control de versión de fuentes (roadmap 5.2)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from ingest.source_versions import get_source_versions
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import models
from app.db.database import get_session
from app.schemas import (
    BreweriesOut,
    BreweryOut,
    SourceVersionOut,
    SourceVersionsOut,
)

router = APIRouter(tags=["breweries", "sources"])


@router.get("/breweries", response_model=BreweriesOut)
def list_breweries(
    country: str | None = Query(default=None, description="Filtrar por país"),
    by_type: str | None = Query(default=None, description="Filtrar por tipo (micro, regional, cidery...)"),
    q: str | None = Query(default=None, description="Búsqueda por nombre/ciudad/estado"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    stmt = select(models.Brewery)
    if country:
        stmt = stmt.where(func.lower(models.Brewery.country) == country.lower().strip())
    if by_type:
        stmt = stmt.where(func.lower(models.Brewery.brewery_type) == by_type.lower().strip())
    if q:
        pattern = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            func.lower(models.Brewery.name).like(pattern)
            | func.lower(models.Brewery.city).like(pattern)
            | func.lower(models.Brewery.state_province).like(pattern)
        )

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.scalar(total_stmt) or 0

    stmt = stmt.order_by(models.Brewery.name.asc()).offset(offset).limit(limit)
    breweries = session.scalars(stmt).all()

    return BreweriesOut(
        total=total,
        items=[BreweryOut.model_validate(b) for b in breweries],
    )


@router.get("/breweries/{brewery_id}", response_model=BreweryOut)
def get_brewery(
    brewery_id: int,
    session: Session = Depends(get_session),
):
    brewery = session.get(models.Brewery, brewery_id)
    if not brewery:
        raise HTTPException(status_code=404, detail="Cervecería no encontrada")
    return BreweryOut.model_validate(brewery)


@router.get("/sources/versions", response_model=SourceVersionsOut)
def list_source_versions(
    session: Session = Depends(get_session),
):
    versions = get_source_versions(session)
    return SourceVersionsOut(
        total=len(versions),
        items=[SourceVersionOut.model_validate(v) for v in versions],
    )
