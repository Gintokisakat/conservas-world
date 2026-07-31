from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.db import models
from app.db.database import get_session
from app.schemas import (
    CategoryOut,
    CountryOut,
    IngredientOut,
    MicrobeOut,
    PaginatedProducts,
    ProductListItem,
    ProductOut,
    RecommendationOut,
    Recommendations,
    ReferenceOut,
    Stats,
    UseRecommendationOut,
)
from ingest.ingredients import CANONICAL_INGREDIENTS, match_ingredients
from ingest.normalize import normalize_name

router = APIRouter()

_SUBSTRATE_NAMES = {
    entry["name"] for entry in CANONICAL_INGREDIENTS if entry.get("substrate", True)
}


def _fts_matches(session: Session, term: str, limit: int = 1000) -> list[int] | None:
    tokens = [t for t in term.split() if t]
    if not tokens:
        return []
    match = " AND ".join(f'"{t}"*' for t in tokens)
    try:
        rows = session.execute(
            text(
                "SELECT rowid FROM products_fts "
                "WHERE products_fts MATCH :t ORDER BY bm25(products_fts) LIMIT :limit"
            ),
            {"t": match, "limit": limit},
        ).scalars().all()
        return list(rows)
    except Exception:
        return None


def _load_product(session: Session, product_id: int) -> models.Product:
    product = session.execute(
        select(models.Product)
        .options(
            selectinload(models.Product.aliases),
            selectinload(models.Product.countries),
            selectinload(models.Product.ingredients),
            selectinload(models.Product.categories),
            selectinload(models.Product.references),
            selectinload(models.Product.microbes),
            selectinload(models.Product.uses),
            selectinload(models.Product.used_by),
        )
        .where(models.Product.id == product_id)
    ).scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


def _product_out(product: models.Product) -> ProductOut:
    out = ProductOut.model_validate(product)
    out.uses = sorted({u.used_product.name for u in product.uses})
    out.used_by = sorted({u.product.name for u in product.used_by})
    return out


def _split_terms(raw: str) -> list[str]:
    return [t.strip() for t in raw.replace(";", ",").split(",") if t.strip()]


@router.get("/products", response_model=PaginatedProducts)
def list_products(
    q: str | None = None,
    category: str | None = Query(default=None, description="Código de categoría"),
    country: str | None = Query(default=None, description="Nombre o código ISO"),
    continent: str | None = None,
    ingredient: str | None = None,
    source: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    session: Session = Depends(get_session),
):
    query = select(models.Product).options(
        selectinload(models.Product.categories),
        selectinload(models.Product.countries),
    )
    count_query = select(func.count()).select_from(models.Product)

    if category:
        cat_query = (
            select(models.Category.id).where(models.Category.code == category).scalar_subquery()
        )
        query = query.where(models.Product.id.in_(
            select(models.product_category.c.product_id).where(
                models.product_category.c.category_id == cat_query
            )
        ))
        count_query = count_query.where(models.Product.id.in_(
            select(models.product_category.c.product_id).where(
                models.product_category.c.category_id == cat_query
            )
        ))
    if country:
        country_query = (
            select(models.Country.id)
            .where(
                (func.lower(models.Country.name) == country.lower())
                | (models.Country.iso2 == country.upper())
                | (models.Country.iso3 == country.upper())
            )
            .scalar_subquery()
        )
        query = query.where(models.Product.id.in_(
            select(models.product_country.c.product_id).where(
                models.product_country.c.country_id == country_query
            )
        ))
        count_query = count_query.where(models.Product.id.in_(
            select(models.product_country.c.product_id).where(
                models.product_country.c.country_id == country_query
            )
        ))
    if continent:
        query = query.where(models.Product.id.in_(
            select(models.product_country.c.product_id)
            .join(models.Country, models.Country.id == models.product_country.c.country_id)
            .where(models.Country.continent == continent)
        ))
        count_query = count_query.where(models.Product.id.in_(
            select(models.product_country.c.product_id)
            .join(models.Country, models.Country.id == models.product_country.c.country_id)
            .where(models.Country.continent == continent)
        ))
    if ingredient:
        ing_query = (
            select(models.Ingredient.id)
            .where(models.Ingredient.name == ingredient.lower())
            .scalar_subquery()
        )
        query = query.where(models.Product.id.in_(
            select(models.product_ingredient.c.product_id).where(
                models.product_ingredient.c.ingredient_id == ing_query
            )
        ))
        count_query = count_query.where(models.Product.id.in_(
            select(models.product_ingredient.c.product_id).where(
                models.product_ingredient.c.ingredient_id == ing_query
            )
        ))
    if source:
        query = query.where(models.Product.source_tag == source)
        count_query = count_query.where(models.Product.source_tag == source)
    if status:
        query = query.where(models.Product.status == status)
        count_query = count_query.where(models.Product.status == status)

    if q:
        fts_ids = _fts_matches(session, q.strip())
        if fts_ids is not None:
            if not fts_ids:
                total = 0
                return PaginatedProducts(total=0, page=page, page_size=page_size, items=[])
            query = query.where(models.Product.id.in_(fts_ids))
            count_query = count_query.where(models.Product.id.in_(fts_ids))
        else:
            term = q.strip().lower()
            query = query.where(
                func.lower(models.Product.name).contains(term)
                | func.lower(func.coalesce(models.Product.description, "")).contains(term)
            )
            count_query = count_query.where(
                func.lower(models.Product.name).contains(term)
                | func.lower(func.coalesce(models.Product.description, "")).contains(term)
            )

    total = session.execute(count_query).scalar_one()
    query = (
        query.order_by(models.Product.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = session.execute(query).scalars().unique().all()
    return PaginatedProducts(
        total=total,
        page=page,
        page_size=page_size,
        items=list(items),
    )


@router.get("/recommendations", response_model=Recommendations)
def recommendations(
    ingredients: str = Query(
        default="", description="Ingredientes/sustratos que tenes (separados por coma)"
    ),
    products: str = Query(
        default="", description="Fermentados que tenes (nombres separados por coma)"
    ),
    session: Session = Depends(get_session),
):
    opts = [
        selectinload(models.Product.categories),
        selectinload(models.Product.countries),
        selectinload(models.Product.ingredients),
    ]

    user_ingredients: set[str] = set()
    for token in _split_terms(ingredients):
        for hit in match_ingredients(token):
            user_ingredients.add(hit["name"])

    make: list[RecommendationOut] = []
    if user_ingredients:
        matched = session.execute(
            select(models.Product)
            .options(*opts)
            .where(models.Product.substrate.in_(user_ingredients))
        ).scalars().all()
        for product in matched:
            names = {i.name for i in product.ingredients}
            core = names & _SUBSTRATE_NAMES
            have = names & user_ingredients
            missing = core - user_ingredients
            make.append(
                RecommendationOut(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    source_tag=product.source_tag,
                    substrate=product.substrate,
                    categories=product.categories,
                    countries=product.countries,
                    matched=sorted(have),
                    missing=sorted(missing),
                )
            )
        make.sort(key=lambda r: len(r.missing))

    use: list[UseRecommendationOut] = []
    product_tokens = [normalize_name(t) for t in _split_terms(products)]
    if product_tokens:
        user_product_ids = set()
        for product in session.execute(
            select(models.Product).options(selectinload(models.Product.aliases))
        ).scalars().all():
            keys = [normalize_name(product.name)] + [
                normalize_name(a.name) for a in product.aliases
            ]
            if any(key in product_tokens for key in keys):
                user_product_ids.add(product.id)
        if user_product_ids:
            used_map: dict[int, list[str]] = {}
            rows = session.execute(
                select(models.ProductUse, models.Product)
                .join(models.Product, models.Product.id == models.ProductUse.product_id)
                .where(models.ProductUse.used_product_id.in_(user_product_ids))
            ).all()
            for product_use, using_product in rows:
                used_map.setdefault(using_product.id, []).append(
                    product_use.used_product.name
                )
            if used_map:
                using_products = session.execute(
                    select(models.Product)
                    .options(*opts)
                    .where(models.Product.id.in_(used_map.keys()))
                ).scalars().all()
                for using_product in using_products:
                    use.append(
                        UseRecommendationOut(
                            id=using_product.id,
                            name=using_product.name,
                            description=using_product.description,
                            source_tag=using_product.source_tag,
                            substrate=using_product.substrate,
                            categories=using_product.categories,
                            countries=using_product.countries,
                            uses_products=sorted(set(used_map[using_product.id])),
                        )
                    )

    return Recommendations(make=make, use=use)


@router.get("/products/random", response_model=ProductOut)
def random_product(session: Session = Depends(get_session)):
    product_id = session.execute(
        select(models.Product.id).order_by(func.random()).limit(1)
    ).scalar_one_or_none()
    if product_id is None:
        raise HTTPException(status_code=404, detail="No hay productos")
    return _product_out(_load_product(session, product_id))


@router.get("/products/{product_id}/related", response_model=list[ProductListItem])
def related_products(
    product_id: int,
    limit: int = Query(default=5, ge=1, le=20),
    session: Session = Depends(get_session),
):
    product = session.execute(
        select(models.Product).where(models.Product.id == product_id)
    ).scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    shared = (
        select(
            models.product_category.c.product_id.label("pid"),
            func.count().label("n"),
        )
        .where(models.product_category.c.category_id.in_(
            select(models.product_category.c.category_id).where(
                models.product_category.c.product_id == product_id
            )
        ))
        .where(models.product_category.c.product_id != product_id)
        .group_by(models.product_category.c.product_id)
        .order_by(func.count().desc())
        .limit(limit)
    )
    rows = session.execute(shared).all()
    ids = [r.pid for r in rows]
    if not ids:
        return []
    related = session.execute(
        select(models.Product)
        .options(
            selectinload(models.Product.categories),
            selectinload(models.Product.countries),
        )
        .where(models.Product.id.in_(ids))
    ).scalars().unique().all()
    order = {pid: i for i, pid in enumerate(ids)}
    return sorted(related, key=lambda p: order[p.id])


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, session: Session = Depends(get_session)):
    return _product_out(_load_product(session, product_id))


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(session: Session = Depends(get_session)):
    return session.execute(
        select(models.Category).order_by(models.Category.name)
    ).scalars().all()


@router.get("/countries", response_model=list[CountryOut])
def list_countries(
    continent: str | None = None,
    session: Session = Depends(get_session),
):
    query = select(models.Country).order_by(models.Country.name)
    if continent:
        query = query.where(models.Country.continent == continent)
    return session.execute(query).scalars().all()


@router.get("/ingredients", response_model=list[IngredientOut])
def list_ingredients(session: Session = Depends(get_session)):
    return session.execute(
        select(models.Ingredient).order_by(models.Ingredient.name)
    ).scalars().all()


@router.get("/references", response_model=list[ReferenceOut])
def list_references(session: Session = Depends(get_session)):
    return session.execute(
        select(models.Reference).order_by(models.Reference.title)
    ).scalars().all()


@router.get("/stats", response_model=Stats)
def stats(session: Session = Depends(get_session)):
    def count(model):
        return session.execute(select(func.count()).select_from(model)).scalar_one()

    by_category = dict(
        session.execute(
            select(models.Category.code, func.count(models.product_category.c.product_id))
            .join(models.product_category, models.product_category.c.category_id == models.Category.id)
            .group_by(models.Category.code)
        ).all()
    )
    by_continent = {
        k: v
        for k, v in session.execute(
            select(models.Country.continent, func.count(models.product_country.c.product_id))
            .join(models.product_country, models.product_country.c.country_id == models.Country.id)
            .group_by(models.Country.continent)
        ).all()
        if k
    }
    by_source = dict(
        session.execute(
            select(models.Product.source_tag, func.count())
            .group_by(models.Product.source_tag)
        ).all()
    )
    return Stats(
        products=count(models.Product),
        countries=count(models.Country),
        ingredients=count(models.Ingredient),
        categories=count(models.Category),
        references=count(models.Reference),
        microbes=count(models.Microbe),
        products_with_ingredients=session.execute(
            select(func.count(func.distinct(models.product_ingredient.c.product_id)))
        ).scalar_one(),
        products_with_substrate=session.execute(
            select(func.count()).select_from(models.Product).where(
                models.Product.substrate.isnot(None)
            )
        ).scalar_one(),
        uses=count(models.ProductUse),
        by_category=by_category,
        by_continent=by_continent,
        by_source=by_source,
    )
