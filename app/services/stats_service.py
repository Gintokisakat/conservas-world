"""Estadísticas globales con caché por fingerprint del dataset.

La base es de solo lectura en producción, así que el resultado se memoiza
mientras el fingerprint (nº de productos activos + última actualización)
no cambie.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import models
from app.db.database import SessionLocal
from app.schemas import Stats

_cache_fingerprint: tuple[int, str] | None = None
_cache_stats: Stats | None = None


def dataset_fingerprint(session: Session) -> tuple:
    """Huella barata de TODAS las tablas que afectan a las estadísticas."""
    from app.services.semantic import _dataset_fingerprint

    prod_fp = _dataset_fingerprint(session)
    extras = []
    for model in (
        models.Country,
        models.Ingredient,
        models.Category,
        models.Reference,
        models.Microbe,
        models.ProductUse,
    ):
        n = session.execute(select(func.count()).select_from(model)).scalar_one()
        extras.append(n)
    return (prod_fp, tuple(extras))


def compute_stats(session: Session, *, use_cache: bool = True) -> Stats:
    global _cache_fingerprint, _cache_stats

    fingerprint = dataset_fingerprint(session)
    if use_cache and _cache_stats is not None and _cache_fingerprint == fingerprint:
        return _cache_stats

    def count(model):
        return session.execute(select(func.count()).select_from(model)).scalar_one()

    def active_count(model, *criteria):
        return session.execute(
            select(func.count())
            .select_from(model)
            .where(model.status != "discarded", *criteria)
        ).scalar_one()

    by_category: dict[str, int] = {
        code: count
        for code, count in session.execute(
            select(models.Category.code, func.count(models.product_category.c.product_id))
            .join(models.product_category, models.product_category.c.category_id == models.Category.id)
            .join(models.Product, models.Product.id == models.product_category.c.product_id)
            .where(models.Product.status != "discarded")
            .group_by(models.Category.code)
        ).all()
    }
    by_continent = {
        k: v
        for k, v in session.execute(
            select(models.Country.continent, func.count(models.product_country.c.product_id))
            .join(models.product_country, models.product_country.c.country_id == models.Country.id)
            .join(models.Product, models.Product.id == models.product_country.c.product_id)
            .where(models.Product.status != "discarded")
            .group_by(models.Country.continent)
        ).all()
        if k
    }
    by_source: dict[str, int] = {
        source: count
        for source, count in session.execute(
            select(models.Product.source_tag, func.count())
            .where(models.Product.status != "discarded")
            .group_by(models.Product.source_tag)
        ).all()
        if source
    }
    stats = Stats(
        products=active_count(models.Product),
        countries=count(models.Country),
        ingredients=count(models.Ingredient),
        categories=count(models.Category),
        references=count(models.Reference),
        microbes=count(models.Microbe),
        products_with_ingredients=session.execute(
            select(func.count(func.distinct(models.product_ingredient.c.product_id)))
            .join(models.Product, models.Product.id == models.product_ingredient.c.product_id)
            .where(models.Product.status != "discarded")
        ).scalar_one(),
        products_with_substrate=active_count(
            models.Product, models.Product.substrate.isnot(None)
        ),
        uses=session.execute(
            select(func.count())
            .select_from(models.ProductUse)
            .join(models.Product, models.Product.id == models.ProductUse.product_id)
            .where(models.Product.status != "discarded")
        ).scalar_one(),
        by_category=by_category,
        by_continent=by_continent,
        by_source=by_source,
    )
    if use_cache:
        _cache_fingerprint = fingerprint
        _cache_stats = stats
    return stats


def reset_cache() -> None:
    global _cache_fingerprint, _cache_stats
    _cache_fingerprint = None
    _cache_stats = None


def warm_stats() -> None:
    session = SessionLocal()
    try:
        compute_stats(session)
    finally:
        session.close()