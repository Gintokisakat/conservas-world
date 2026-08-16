import csv
import html as html_mod
import io
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from ingest.ingredients import CANONICAL_INGREDIENTS, match_ingredients
from ingest.normalize import normalize_name
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.db import models
from app.db.database import get_session
from app.schemas import (
    CategoryOut,
    CheeseMetagenomeOut,
    CountryOut,
    DairyFermentOut,
    GeoPointOut,
    GlossaryOut,
    IngredientOut,
    MicrobeOut,
    NutritionOut,
    PaginatedProducts,
    ProductListItem,
    ProductOut,
    RecommendationOut,
    Recommendations,
    ReferenceOut,
    SearchSuggest,
    SeasonalMonthName,
    SeasonalOut,
    Stats,
    SuggestItem,
    UseRecommendationOut,
)
from app.services.diet import DIET_TAGS, REQUIRED, VIOLATIONS, product_diet_tags

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
            selectinload(models.Product.dairy),
            selectinload(models.Product.metagenome),
        )
        .where(models.Product.id == product_id)
    ).scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


def _dairy_out(dairy: models.DairyFerment | None) -> DairyFermentOut | None:
    if dairy is None:
        return None
    microbiota = []
    if dairy.microbiota_json:
        try:
            microbiota = json.loads(dairy.microbiota_json)
        except json.JSONDecodeError:
            microbiota = []
    return DairyFermentOut(
        classification=dairy.classification,
        country=dairy.country,
        region=dairy.region,
        milk_type=dairy.milk_type,
        treatment=dairy.treatment,
        ripening=dairy.ripening,
        microbiota=microbiota,
        geographical_indication=bool(dairy.geographical_indication),
        characteristics=dairy.characteristics,
    )


def _metagenome_out(meta: models.CheeseMetagenome | None) -> CheeseMetagenomeOut | None:
    if meta is None:
        return None
    taxa = []
    if meta.taxa_json:
        try:
            taxa = json.loads(meta.taxa_json)
        except json.JSONDecodeError:
            taxa = []
    return CheeseMetagenomeOut(
        subtype=meta.subtype,
        sample_count=meta.sample_count,
        taxa=taxa,
        url=meta.url,
    )


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
        "image_url": product.image_url,
        "aliases": product.aliases,
        "countries": product.countries,
        "ingredients": product.ingredients,
        "categories": product.categories,
        "microbes": product.microbes,
        "references": product.references,
        "uses": sorted({u.used_product.name for u in product.uses if u.used_product}),
        "used_by": sorted({u.product.name for u in product.used_by if u.product}),
        "diet_tags": product_diet_tags(product.ingredients),
        "dairy": _dairy_out(product.dairy),
        "metagenome": _metagenome_out(product.metagenome),
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
        image_url=product.image_url,
        categories=product.categories,
        countries=product.countries,
        diet_tags=product_diet_tags(product.ingredients),
        geographical_indication=bool(product.dairy and product.dairy.geographical_indication),
    )


def _apply_filters(query, count_query, session, *, q, category, country, continent,
                   ingredient, source, fermentation_time, diet, status, gi=False):
    """Aplica los filtros comunes de listado a `query` y `count_query`."""
    if gi:
        gi_query = (
            select(models.DairyFerment.product_id)
            .where(models.DairyFerment.geographical_indication.is_(True))
        )
        query = query.where(models.Product.id.in_(gi_query))
        count_query = count_query.where(models.Product.id.in_(gi_query))

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
    return query, count_query


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
    gi: bool = Query(default=False, description="Solo productos con indicación geográfica"),
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    session: Session = Depends(get_session),
):
    query = select(models.Product).options(
        selectinload(models.Product.categories),
        selectinload(models.Product.countries),
        selectinload(models.Product.ingredients),
        selectinload(models.Product.dairy),
    )
    count_query = select(func.count()).select_from(models.Product)

    query, count_query = _apply_filters(
        query, count_query, session,
        q=q, category=category, country=country, continent=continent,
        ingredient=ingredient, source=source, fermentation_time=fermentation_time,
        diet=diet, status=status, gi=gi,
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
        items=[_list_item(p) for p in items],
    )


@router.get("/products/geo", response_model=list[GeoPointOut])
def list_products_geo(
    q: str | None = None,
    category: str | None = Query(default=None, description="Código de categoría"),
    country: str | None = Query(default=None, description="Nombre o código ISO"),
    continent: str | None = None,
    ingredient: str | None = None,
    source: str | None = None,
    fermentation_time: str | None = None,
    diet: str | None = Query(default=None),
    gi: bool = Query(default=False, description="Solo productos con indicación geográfica"),
    limit: int = Query(default=4000, ge=1, le=20000),
    session: Session = Depends(get_session),
):
    query = select(models.Product).options(
        selectinload(models.Product.categories),
        selectinload(models.Product.countries),
    )
    count_query = select(func.count()).select_from(models.Product)
    query, count_query = _apply_filters(
        query, count_query, session,
        q=q, category=category, country=country, continent=continent,
        ingredient=ingredient, source=source, fermentation_time=fermentation_time,
        diet=diet, status=None, gi=gi,
    )
    rows = session.execute(
        query.order_by(models.Product.name).limit(limit)
    ).scalars().unique().all()

    points: list[GeoPointOut] = []
    for p in rows:
        for c in p.countries:
            if c.latitude is None or c.longitude is None:
                continue
            points.append(
                GeoPointOut(
                    id=p.id,
                    name=p.name,
                    lat=c.latitude,
                    lng=c.longitude,
                    country=c.name,
                    continent=c.continent,
                    category=p.categories[0].name if p.categories else None,
                    source_tag=p.source_tag,
                    substrate=p.substrate,
                )
            )
    return points


@router.get("/search/suggest", response_model=SearchSuggest)
def search_suggest(
    q: str = Query(default=""),
    limit: int = Query(default=10, ge=1, le=20),
    session: Session = Depends(get_session),
):
    term = q.strip()
    if not term:
        return SearchSuggest()

    products: list[SuggestItem] = []
    ingredients: list[SuggestItem] = []

    fts_ids = _fts_matches(session, term, limit=50)
    if fts_ids is not None and fts_ids:
        rows = session.execute(
            select(models.Product)
            .options(
                selectinload(models.Product.categories),
                selectinload(models.Product.countries),
            )
            .where(models.Product.id.in_(fts_ids), models.Product.status != "discarded")
        ).scalars().all()
    else:
        like = f"%{term.lower()}%"
        rows = session.execute(
            select(models.Product)
            .options(
                selectinload(models.Product.categories),
                selectinload(models.Product.countries),
            )
            .where(
                models.Product.status != "discarded",
                func.lower(models.Product.name).like(like),
            )
        ).scalars().all()

    def _rank(product):
        name = product.name.lower()
        if name.startswith(term.lower()):
            return (0, name)
        return (1, name)

    for p in sorted(rows, key=_rank)[:limit]:
        products.append(
            SuggestItem(
                type="product",
                id=p.id,
                name=p.name,
                category=p.categories[0].name if p.categories else None,
                country=p.countries[0].name if p.countries else None,
                substrate=p.substrate,
            )
        )

    prefix = f"{term.lower()}%"
    ing_rows = session.execute(
        select(models.Ingredient)
        .where(func.lower(models.Ingredient.name).like(prefix))
        .order_by(models.Ingredient.name)
        .limit(limit)
    ).scalars().all()
    for ing in ing_rows:
        ingredients.append(
            SuggestItem(
                type="ingredient",
                id=ing.id,
                name=ing.name,
                category=ing.category,
            )
        )
    if len(ing_rows) < limit:
        contains = f"%{term.lower()}%"
        extra = session.execute(
            select(models.Ingredient)
            .where(
                func.lower(models.Ingredient.name).like(contains),
                func.lower(models.Ingredient.name).notlike(prefix),
            )
            .order_by(models.Ingredient.name)
            .limit(limit - len(ing_rows))
        ).scalars().all()
        ingredients.extend(
            SuggestItem(
                type="ingredient",
                id=ing.id,
                name=ing.name,
                category=ing.category,
            )
            for ing in extra
        )

    terms: list[SuggestItem] = []
    glossary_like = f"%{term.lower()}%"
    term_rows = session.execute(
        select(models.GlossaryTerm)
        .where(func.lower(models.GlossaryTerm.term).like(glossary_like))
        .order_by(models.GlossaryTerm.term)
        .limit(limit)
    ).scalars().all()
    for gl in term_rows:
        terms.append(
            SuggestItem(
                type="glossary",
                id=gl.id,
                name=gl.term,
                category=gl.language,
            )
        )

    return SearchSuggest(products=products, ingredients=ingredients, glossary=terms)


@router.get("/glossary", response_model=list[GlossaryOut])
def list_glossary(
    q: str = Query(default="", description="Filtro por término (prefijo/contiene)"),
    lang: str = Query(default="es", pattern="^(es|en)$"),
    limit: int = Query(default=100, ge=1, le=500),
    product_id: int | None = Query(default=None, description="Filtrar por producto relacionado"),
    session: Session = Depends(get_session),
):
    query = select(models.GlossaryTerm).where(models.GlossaryTerm.language == lang)
    if q.strip():
        needle = f"%{q.strip().lower()}%"
        query = query.where(func.lower(models.GlossaryTerm.term).like(needle))
    if product_id is not None:
        query = query.where(models.GlossaryTerm.related_product_id == product_id)
    rows = session.execute(
        query.order_by(models.GlossaryTerm.term).limit(limit)
    ).scalars().all()
    return [
        GlossaryOut(
            id=g.id,
            term=g.term,
            definition=g.definition,
            language=g.language,
            related_product_id=g.related_product_id,
            related_product=g.related_product.name if g.related_product else None,
        )
        for g in rows
    ]


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
        for row in session.execute(
            select(models.Product.id, models.Product.name)
            .where(models.Product.status != "discarded")
        ).all():
            if normalize_name(row.name) in product_tokens:
                user_product_ids.add(row.id)
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


@router.get("/products/dairy", response_model=PaginatedProducts)
def list_dairy_products(
    gi: bool = Query(default=False, description="Solo con indicación geográfica"),
    classification: str | None = Query(
        default=None, description="cheese, fermented milk o yogurt"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    session: Session = Depends(get_session),
):
    query = select(models.Product).options(
        selectinload(models.Product.categories),
        selectinload(models.Product.countries),
        selectinload(models.Product.ingredients),
        selectinload(models.Product.dairy),
    )
    count_query = select(func.count()).select_from(models.Product)
    query = query.where(
        models.Product.id.in_(select(models.DairyFerment.product_id))
    )
    count_query = count_query.where(
        models.Product.id.in_(select(models.DairyFerment.product_id))
    )
    if gi:
        gi_query = select(models.DairyFerment.product_id).where(
            models.DairyFerment.geographical_indication.is_(True)
        )
        query = query.where(models.Product.id.in_(gi_query))
        count_query = count_query.where(models.Product.id.in_(gi_query))
    if classification:
        class_query = select(models.DairyFerment.product_id).where(
            models.DairyFerment.classification == classification
        )
        query = query.where(models.Product.id.in_(class_query))
        count_query = count_query.where(models.Product.id.in_(class_query))

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
            selectinload(models.Product.dairy),
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


_EXPORT_LABELS = {
    "es": {
        "name": "Nombre",
        "image": "Imagen",
        "aliases": "Alias",
        "description": "Descripción",
        "method": "Método",
        "fermentation_time": "Tiempo de fermentación",
        "storage_life": "Conservación",
        "categories": "Categorías",
        "countries": "Países",
        "ingredients": "Ingredientes",
        "microbes": "Microbios",
        "diet_tags": "Etiquetas dietarias",
        "references": "Referencias",
        "uses": "Se usa como ingrediente en",
        "used_by": "Es ingrediente de",
        "gi": "Indicación geográfica",
    },
    "en": {
        "name": "Name",
        "image": "Image",
        "aliases": "Aliases",
        "description": "Description",
        "method": "Method",
        "fermentation_time": "Fermentation time",
        "storage_life": "Storage & shelf life",
        "categories": "Categories",
        "countries": "Countries",
        "ingredients": "Ingredients",
        "microbes": "Microbes",
        "diet_tags": "Dietary tags",
        "references": "References",
        "uses": "Used as ingredient in",
        "used_by": "Is ingredient of",
        "gi": "Geographical indication",
    },
}


def _export_rows(data: ProductOut, lang: str) -> list[tuple[str, str]]:
    labels = _EXPORT_LABELS.get(lang, _EXPORT_LABELS["es"])

    def join(items) -> str:
        return ", ".join(str(i) for i in items)

    values = {
        "name": data.name,
        "image": data.image_url or "",
        "aliases": join(a.name for a in data.aliases),
        "description": data.description or "",
        "method": data.method or "",
        "fermentation_time": data.fermentation_time or "",
        "storage_life": data.storage_life or "",
        "categories": join(c.name for c in data.categories),
        "countries": join(c.name for c in data.countries),
        "ingredients": join(i.name for i in data.ingredients),
        "microbes": join(m.name for m in data.microbes),
        "diet_tags": join(data.diet_tags),
        "references": "; ".join(r.title for r in data.references),
        "uses": join(data.uses),
        "used_by": join(data.used_by),
        "gi": "Sí" if data.dairy and data.dairy.geographical_indication else "No",
    }
    return [(labels[k], v) for k, v in values.items()]


def _render_recipe_html(data: ProductOut, lang: str) -> str:
    t = {
        "title": "Recipe Sheet" if lang == "en" else "Ficha de la receta",
        "method": "Traditional Method" if lang == "en" else "Método tradicional",
        "time": "Fermentation Time" if lang == "en" else "Tiempo de fermentación",
        "storage": "Storage" if lang == "en" else "Conservación",
        "ingredients": "Key Ingredients" if lang == "en" else "Ingredientes clave",
        "microbes": "Fermenting Microbes" if lang == "en" else "Microbios fermentadores",
        "references": "References & Sources" if lang == "en" else "Referencias y fuentes",
        "diet": "Dietary Tags" if lang == "en" else "Etiquetas dietarias",
        "print": "Print / Save as PDF" if lang == "en" else "Imprimir / Guardar como PDF",
        "safety": (
            "Food Safety: target pH < 4.6 for lactic/acetic fermentation"
            if lang == "en"
            else "Seguridad alimentaria: pH objetivo < 4.6 para fermentación láctica/acética"
        ),
        "footer": "Conservas del Mundo" if lang == "en" else "Conservas del Mundo",
        "gi": (
            "Geographical Indication (PDO)"
            if lang == "en"
            else "Indicación geográfica (DOP)"
        ),
    }

    def li(items):
        return "".join(f"<li>{html_mod.escape(str(i))}</li>" for i in items)

    tags = "".join(
        f'<span class="tag">{html_mod.escape(str(x))}</span>'
        for x in list(data.diet_tags) + [c.name for c in data.countries]
    )
    if data.dairy and data.dairy.geographical_indication:
        tags += f'<span class="tag gi">{html_mod.escape(t["gi"])}</span>'
    ingredients = li(i.name for i in data.ingredients) if data.ingredients else "<li>—</li>"
    microbes = li(m.name for m in data.microbes) if data.microbes else "<li>—</li>"
    refs = (
        "".join(f"<li>{html_mod.escape(r.title)}</li>" for r in data.references)
        if data.references
        else "<li>—</li>"
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{html_mod.escape(data.name)}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Georgia, 'Times New Roman', serif; color: #1f2721; padding: 2rem; max-width: 720px; margin: 0 auto; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 0.3rem; }}
  .meta {{ color: #566359; margin-bottom: 1rem; }}
  .tags {{ margin: 0.6rem 0 1.2rem; }}
  .tag {{ display: inline-block; background: #eaf2eb; color: #225232; border-radius: 999px; padding: 0.15rem 0.6rem; font-size: 0.75rem; margin-right: 0.3rem; }}
  .tag.gi {{ background: #eef0fb; color: #3b3f8f; border: 1px solid #c7cbea; }}
  .field {{ margin-bottom: 1.1rem; }}
  .field h3 {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.06em; color: #88968b; margin-bottom: 0.25rem; }}
  ul {{ padding-left: 1.2rem; }}
  li {{ margin-bottom: 0.15rem; line-height: 1.45; }}
  p {{ line-height: 1.5; }}
  .safety {{ background: #fff8eb; border: 1px solid #e5ded2; border-radius: 8px; padding: 0.7rem 0.9rem; font-size: 0.85rem; color: #8c4217; margin-top: 1.5rem; }}
  .btn {{ margin-top: 1.5rem; font-family: inherit; font-size: 0.9rem; padding: 0.5rem 1rem; border-radius: 8px; border: 1.5px solid #2d5a3f; background: #2d5a3f; color: #fff; cursor: pointer; }}
  footer {{ margin-top: 2rem; font-size: 0.8rem; color: #88968b; border-top: 1px solid #e5ded2; padding-top: 0.6rem; }}
  @media print {{
    .btn {{ display: none; }}
    body {{ padding: 0; }}
    .safety {{ page-break-inside: avoid; }}
  }}
  .hero {{ display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1rem; }}
  .hero img {{ width: 140px; height: 140px; object-fit: cover; border-radius: 10px; }}
  @media (max-width: 480px) {{ .hero {{ flex-direction: column; }} .hero img {{ width: 100%; height: auto; }} }}
</style>
</head>
<body>
  <button type="button" class="btn" onclick="window.print()">🖨️ {t['print']}</button>
  <div class="hero">
    {f'<img src="{html_mod.escape(data.image_url)}" alt="{html_mod.escape(data.name)}">' if data.image_url else ""}
    <div>
      <h1>{html_mod.escape(data.name)}</h1>
      <div class="meta">{html_mod.escape(data.substrate or "")}</div>
    </div>
  </div>
  <div class="tags">{tags}</div>
  {f"<div class='field'><h3>{t['method']}</h3><p>{html_mod.escape(data.method)}</p></div>" if data.method else ""}
  <div class="field"><h3>{t['ingredients']}</h3><ul>{ingredients}</ul></div>
  {f"<div class='field'><h3>{t['time']}</h3><p>{html_mod.escape(data.fermentation_time)}</p></div>" if data.fermentation_time else ""}
  {f"<div class='field'><h3>{t['storage']}</h3><p>{html_mod.escape(data.storage_life)}</p></div>" if data.storage_life else ""}
  {f"<div class='field'><h3>{t['microbes']}</h3><ul>{microbes}</ul></div>" if data.microbes else ""}
  {f"<div class='field'><h3>{t['diet']}</h3><ul>{li(data.diet_tags)}</ul></div>" if data.diet_tags else ""}
  {f"<div class='field'><h3>{t['references']}</h3><ul>{refs}</ul></div>" if data.references else ""}
  <div class="safety">🛡️ {t['safety']}</div>
  <footer>{t['footer']} · {html_mod.escape(data.source_tag or "")}</footer>
</body>
</html>"""


@router.get("/products/{product_id}/export")
def export_product(
    product_id: int,
    format: str = Query(default="csv", pattern="^(csv|pdf|html)$"),
    lang: str = Query(default="es", pattern="^(es|en)$"),
    session: Session = Depends(get_session),
):
    data = _product_out(_load_product(session, product_id), lang=lang)

    if format == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Campo", "Valor"] if lang == "es" else ["Field", "Value"])
        writer.writerows(_export_rows(data, lang))
        content = "\ufeff" + buf.getvalue()
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="producto-{product_id}.csv"'
            },
        )

    html_doc = _render_recipe_html(data, lang)
    return Response(
        content=html_doc,
        media_type="text/html; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="producto-{product_id}.html"'
        },
    )


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


@router.get("/ingredients/{ingredient_id}/nutrition", response_model=NutritionOut | None)
def ingredient_nutrition(
    ingredient_id: int,
    response: Response,
    session: Session = Depends(get_session),
):
    ingredient = session.execute(
        select(models.Ingredient).where(models.Ingredient.id == ingredient_id)
    ).scalar_one_or_none()
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    nutrition = session.execute(
        select(models.NutritionData).where(
            models.NutritionData.ingredient_id == ingredient_id
        )
    ).scalar_one_or_none()
    if nutrition is None:
        return None
    response.headers["Cache-Control"] = "public, max-age=86400"
    return nutrition


@router.get("/diets")
def list_diets(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return DIET_TAGS


_SEASONAL_PATH = Path(__file__).resolve().parents[2] / "data" / "seasonal.json"
_seasonal_cache: dict | None = None

_MONTH_NAMES = {
    1: SeasonalMonthName(es="enero", en="January"),
    2: SeasonalMonthName(es="febrero", en="February"),
    3: SeasonalMonthName(es="marzo", en="March"),
    4: SeasonalMonthName(es="abril", en="April"),
    5: SeasonalMonthName(es="mayo", en="May"),
    6: SeasonalMonthName(es="junio", en="June"),
    7: SeasonalMonthName(es="julio", en="July"),
    8: SeasonalMonthName(es="agosto", en="August"),
    9: SeasonalMonthName(es="septiembre", en="September"),
    10: SeasonalMonthName(es="octubre", en="October"),
    11: SeasonalMonthName(es="noviembre", en="November"),
    12: SeasonalMonthName(es="diciembre", en="December"),
}


def _load_seasonal() -> dict:
    global _seasonal_cache
    if _seasonal_cache is None:
        _seasonal_cache = json.loads(_SEASONAL_PATH.read_text(encoding="utf-8"))
    return _seasonal_cache


@router.get("/seasonal", response_model=SeasonalOut)
def seasonal(
    response: Response,
    month: int = Query(default=datetime.now().month, ge=1, le=12),
    continent: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    session: Session = Depends(get_session),
):
    response.headers["Cache-Control"] = "public, max-age=86400"

    seasonal = _load_seasonal()
    in_season = [name for name, months in seasonal["ingredients"].items() if month in months]

    ing_rows = session.execute(
        select(models.Ingredient.id, models.Ingredient.name).where(
            models.Ingredient.name.in_(in_season)
        )
    ).all()
    if not ing_rows:
        return SeasonalOut(
            month=month, month_name=_MONTH_NAMES[month], total=0, ingredients=[], products=[]
        )

    ing_ids = [r.id for r in ing_rows]
    ing_name = {r.id: r.name for r in ing_rows}

    matches = (
        select(models.product_ingredient.c.product_id, models.product_ingredient.c.ingredient_id)
        .join(models.Product, models.Product.id == models.product_ingredient.c.product_id)
        .where(
            models.Product.status != "discarded",
            models.product_ingredient.c.ingredient_id.in_(ing_ids),
        )
    )
    if continent:
        matches = (
            matches.join(
                models.product_country, models.product_country.c.product_id == models.Product.id
            )
            .join(models.Country, models.Country.id == models.product_country.c.country_id)
            .where(models.Country.continent == continent)
        )

    counts: dict[int, int] = {}
    product_ids: set[int] = set()
    for pid, iid in session.execute(matches).all():
        counts[iid] = counts.get(iid, 0) + 1
        product_ids.add(pid)

    ingredient_counts = sorted(
        (
            {"name": ing_name[iid], "count": count}
            for iid, count in counts.items()
            if count > 0
        ),
        key=lambda item: (-item["count"], item["name"]),
    )

    products = session.execute(
        select(models.Product)
        .options(
            selectinload(models.Product.categories),
            selectinload(models.Product.countries),
            selectinload(models.Product.ingredients),
            selectinload(models.Product.dairy),
        )
        .where(models.Product.id.in_(product_ids))
        .order_by(models.Product.name)
        .limit(limit)
    ).scalars().all()

    return SeasonalOut(
        month=month,
        month_name=_MONTH_NAMES[month],
        total=len(product_ids),
        ingredients=ingredient_counts,
        products=[_list_item(p) for p in products],
    )


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
