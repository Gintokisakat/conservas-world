from fastapi import APIRouter, Depends, HTTPException, Query, Response
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
from app.services.diet import DIET_TAGS, REQUIRED, VIOLATIONS, product_diet_tags
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


def _product_out(product: models.Product, lang: str = "es") -> ProductOut:
    p_name = product.name
    if lang == "en" and product.aliases:
        en_alias = next((a.name for a in product.aliases if a.language in ("en", "orig")), None)
        if en_alias:
            p_name = en_alias

    data = {
        "id": product.id,
        "name": p_name,
        "description": product.description,
        "method": product.method,
        "fermentation_time": product.fermentation_time,
        "storage_life": product.storage_life,
        "status": product.status,
        "source_tag": product.source_tag,
        "substrate": product.substrate,
        "aliases": product.aliases,
        "countries": product.countries,
        "ingredients": product.ingredients,
        "categories": product.categories,
        "microbes": product.microbes,
        "references": product.references,
        "uses": sorted({u.used_product.name for u in product.uses if u.used_product}),
        "used_by": sorted({u.product.name for u in product.used_by if u.product}),
        "diet_tags": product_diet_tags(product.ingredients),
    }
    return ProductOut.model_validate(data)


def _split_terms(raw: str) -> list[str]:
    return [t.strip() for t in raw.replace(";", ",").split(",") if t.strip()]


def _diet_ids(session: Session, diet: str) -> list[int] | None:
    """IDs de productos que cumplen la etiqueta dietaria (None = etiqueta inválida)."""
    if diet not in DIET_TAGS:
        return None
    if diet == "spicy":
        required = REQUIRED[diet]
        rows = session.execute(
            select(models.product_ingredient.c.product_id)
            .join(models.Ingredient, models.Ingredient.id == models.product_ingredient.c.ingredient_id)
            .where(models.Ingredient.name.in_(required))
        ).scalars().all()
        return list(set(rows))
    blocked = VIOLATIONS[diet]
    rows = session.execute(
        select(models.Product.id).where(
            models.Product.id.in_(
                select(models.product_ingredient.c.product_id)
                .join(models.Ingredient, models.Ingredient.id == models.product_ingredient.c.ingredient_id)
                .where(models.Ingredient.name.in_(blocked))
            )
        )
    ).scalars().all()
    blocked_ids = set(rows)
    all_ids = session.execute(
        select(models.Product.id).where(models.Product.status != "discarded")
    ).scalars().all()
    return [pid for pid in all_ids if pid not in blocked_ids]


def _list_item(product: models.Product) -> ProductListItem:
    return ProductListItem(
        id=product.id,
        name=product.name,
        description=product.description,
        source_tag=product.source_tag,
        substrate=product.substrate,
        categories=product.categories,
        countries=product.countries,
        diet_tags=product_diet_tags(product.ingredients),
    )


@router.get("/products", response_model=PaginatedProducts)
def list_products(
    q: str | None = None,
    category: str | None = Query(default=None, description="Código de categoría"),
    country: str | None = Query(default=None, description="Nombre o código ISO"),
    continent: str | None = None,
    ingredient: str | None = None,
    source: str | None = None,
    fermentation_time: str | None = None,
    diet: str | None = Query(
        default=None,
        description="Filtro por etiqueta dietaria: vegan, vegetarian, gluten_free, dairy_free, soy_free, nut_free, egg_free, pescatarian, spicy",
    ),
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    session: Session = Depends(get_session),
):
    query = select(models.Product).options(
        selectinload(models.Product.categories),
        selectinload(models.Product.countries),
        selectinload(models.Product.ingredients),
    )
    count_query = select(func.count()).select_from(models.Product)

    if diet:
        diet_ids = _diet_ids(session, diet)
        if diet_ids is None:
            raise HTTPException(status_code=400, detail=f"Etiqueta dietaria inválida: {diet}")
        query = query.where(models.Product.id.in_(diet_ids))
        count_query = count_query.where(models.Product.id.in_(diet_ids))

    if fermentation_time:
        query = query.where(func.lower(models.Product.fermentation_time).contains(fermentation_time.lower()))
        count_query = count_query.where(func.lower(models.Product.fermentation_time).contains(fermentation_time.lower()))

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
    else:
        query = query.where(models.Product.status != "discarded")
        count_query = count_query.where(models.Product.status != "discarded")

    if q:
        fts_ids = _fts_matches(session, q.strip())
        if fts_ids is not None and fts_ids:
            query = query.where(models.Product.id.in_(fts_ids))
            count_query = count_query.where(models.Product.id.in_(fts_ids))
        else:
            term = q.strip().lower()
            norm_term = normalize_name(q.strip())
            search_clause = (
                func.lower(models.Product.name).contains(term)
                | func.lower(func.coalesce(models.Product.description, "")).contains(term)
                | func.lower(models.Product.name).contains(norm_term)
            )
            query = query.where(search_clause)
            count_query = count_query.where(search_clause)

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
        items=[_list_item(p) for p in items],
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
            .where(
                models.Product.substrate.in_(user_ingredients),
                models.Product.status != "discarded",
            )
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
        user_product_ids: set[int] = set()
        for product in session.execute(
            select(models.Product.id, models.Product.name)
            .where(models.Product.status != "discarded")
        ).all():
            if normalize_name(product.name) in product_tokens:
                user_product_ids.add(product.id)
        for alias_row in session.execute(
            select(models.ProductAlias.product_id, models.ProductAlias.name)
        ).all():
            if normalize_name(alias_row.name) in product_tokens:
                user_product_ids.add(alias_row.product_id)
        if user_product_ids:
            used_map: dict[int, list[str]] = {}
            rows = session.execute(
                select(models.ProductUse, models.Product)
                .join(models.Product, models.Product.id == models.ProductUse.product_id)
                .where(
                    models.ProductUse.used_product_id.in_(user_product_ids),
                    models.Product.status != "discarded",
                )
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
        select(models.Product.id)
        .where(models.Product.status != "discarded")
        .order_by(func.random())
        .limit(1)
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
        .where(models.Product.id.in_(ids), models.Product.status != "discarded")
    ).scalars().unique().all()
    order = {pid: i for i, pid in enumerate(ids)}
    return sorted(related, key=lambda p: order[p.id])


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    lang: str = Query(default="es", description="Idioma del contenido (es / en)"),
    session: Session = Depends(get_session),
):
    return _product_out(_load_product(session, product_id), lang=lang)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(response: Response, session: Session = Depends(get_session)):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return session.execute(
        select(models.Category).order_by(models.Category.name)
    ).scalars().all()


@router.get("/countries", response_model=list[CountryOut])
def list_countries(
    response: Response,
    continent: str | None = None,
    session: Session = Depends(get_session),
):
    response.headers["Cache-Control"] = "public, max-age=3600"
    query = select(models.Country).order_by(models.Country.name)
    if continent:
        query = query.where(models.Country.continent == continent)
    return session.execute(query).scalars().all()


@router.get("/ingredients", response_model=list[IngredientOut])
def list_ingredients(response: Response, session: Session = Depends(get_session)):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return session.execute(
        select(models.Ingredient).order_by(models.Ingredient.name)
    ).scalars().all()


@router.get("/diets")
def list_diets(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return DIET_TAGS


@router.get("/microbes", response_model=list[MicrobeOut])
def list_microbes(response: Response, session: Session = Depends(get_session)):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return session.execute(
        select(models.Microbe).order_by(models.Microbe.name)
    ).scalars().all()


@router.get("/references", response_model=list[ReferenceOut])
def list_references(response: Response, session: Session = Depends(get_session)):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return session.execute(
        select(models.Reference).order_by(models.Reference.title)
    ).scalars().all()


@router.get("/stats", response_model=Stats)
def stats(session: Session = Depends(get_session)):
    def count(model):
        return session.execute(select(func.count()).select_from(model)).scalar_one()

    def active_count(model, *criteria):
        return session.execute(
            select(func.count())
            .select_from(model)
            .where(model.status != "discarded", *criteria)
        ).scalar_one()

    by_category = dict(
        session.execute(
            select(models.Category.code, func.count(models.product_category.c.product_id))
            .join(models.product_category, models.product_category.c.category_id == models.Category.id)
            .join(models.Product, models.Product.id == models.product_category.c.product_id)
            .where(models.Product.status != "discarded")
            .group_by(models.Category.code)
        ).all()
    )
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
    by_source = dict(
        session.execute(
            select(models.Product.source_tag, func.count())
            .where(models.Product.status != "discarded")
            .group_by(models.Product.source_tag)
        ).all()
    )
    return Stats(
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
