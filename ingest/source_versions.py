"""Control y auditoría de versión de fuentes de ingesta (roadmap 5.2)."""

from datetime import datetime

from app.db import models
from sqlalchemy import select
from sqlalchemy.orm import Session


def record_source_version(
    session: Session,
    source: str,
    records_count: int,
    checksum: str | None = None,
    status: str = "active",
) -> models.SourceVersion:
    """Registra o actualiza la versión de ingesta de una fuente de datos."""
    source_clean = source.strip().lower()
    existing = session.scalars(
        select(models.SourceVersion).where(models.SourceVersion.source == source_clean)
    ).first()

    if existing:
        existing.fetched_at = datetime.now()
        existing.records_count = records_count
        existing.checksum = checksum
        existing.status = status
        record = existing
    else:
        record = models.SourceVersion(
            source=source_clean,
            records_count=records_count,
            checksum=checksum,
            status=status,
        )
        session.add(record)

    session.commit()
    session.refresh(record)
    return record


def get_source_versions(session: Session) -> list[models.SourceVersion]:
    """Retorna todas las versiones de fuentes registradas."""
    return session.scalars(
        select(models.SourceVersion).order_by(models.SourceVersion.source.asc())
    ).all()
