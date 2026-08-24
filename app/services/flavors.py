"""Clasificación heurística de productos por perfil de sabor (3.6 Mapa de sabores).

Cada eje de sabor se puntúa contando coincidencias de keywords en el nombre,
el método y los ingredientes del producto. Sin ML: lo suficientemente preciso
para una visualización agregada por continente/categoría.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import models

AXES = ["picante", "ácido", "umami", "dulce", "salado", "amargo", "fermentado"]

KEYWORDS: dict[str, tuple[str, ...]] = {
    "picante": (
        "chile", "chili", "aji", "ají", "guindilla", "pimiento", "pepper", "wasabi",
        "wasabia", "chutney", "harissa", "gochujang", "sambal", "sriracha", "pimenton", "cayena",
    ),
    "ácido": (
        "vinagre", "vinegar", "pickle", "encurtid", "acid", "ácido", "limón", "lemon", "lime",
        "lima", "citric", "cítric", "sourdough", "sauer", "agrio", "sour", "kimchi", "kombucha",
        "shrub", "acetic",
    ),
    "umami": (
        "miso", "soja", "soy", "shoyu", "tamari", "fish sauce", "nam pla", "worcestershire",
        "mushroom", "seta", "hongos", "tomate", "tomato", "anchoa", "anchovy", "garum",
        "parmesano", "parmesan", "pecorino", "marmite", "algas", "seaweed", "kombu", "dashi",
    ),
    "dulce": (
        "miel", "honey", "azúcar", "sugar", "caramelo", "caramel", "dulce", "sweet", "jalea",
        "jam", "mermelada", "conserva", "fruta", "fruit", "coco", "coconut", "melon", "dátil",
        "date", "mango", "uva", "grape", "pera", "pear", "manzana", "apple", "albaricoque",
        "apricot", "cereza", "cherry", "higo", "fig",
    ),
    "salado": (
        "sal", "salt", "salmuera", "brine", "en sal", "curado", "cured", "salmuerado",
        "salazón", "salted", "salmón", "salmon", "bacalao", "cod", "prosciutto", "jamón",
        "ham", "salami", "anchoa", "anchovy",
    ),
    "amargo": (
        "amargo", "bitter", "ruibarbo", "rhubarb", "cidra", "naranja", "orange", "pomelo",
        "grapefruit", "col", "kale", "berza", "rúcula", "arugula", "cerveza", "beer", "hops",
        "lúpulo", "café", "coffee", "cacao", "cocoa",
    ),
    "fermentado": (
        "ferment", "fermentado", "fermentation", "lacto", "lactic", "koji", "natto", "tempeh",
        "miso", "kombucha", "kefir", "kimchi", "sauerkraut", "chucrut", "yogur", "yogurt",
        "massa madre", "sourdough", "garum", "idli", "dosai", "dosa",
    ),
}

KEYWORD_BONUSES: dict[str, tuple[str, ...]] = {
    # Nombres de producto que indican inequívocamente un perfil dominante
    "picante": ("ajiaco", "pepper sauce", "salsa picante", "hot sauce", "gochujang", "sambal"),
    "ácido": ("pickles", "pickled", "escabeche", "vinaigrette", "agrio"),
    "umami": ("miso", "fish sauce", "garum", "soy sauce", "worcestershire"),
    "dulce": ("mermelada", "jam", "jelly", "honey", "sweet pickle"),
    "salado": ("salazón", "salt-cured", "brined", "cured fish", "salted"),
    "amargo": ("bitter", "amaro", "bitters"),
    "fermentado": ("kombucha", "kimchi", "sauerkraut", "kefir", "tempeh", "natto"),
}


def _normalize(text: str) -> str:
    return text.lower()


def flavor_profile(name: str, method: str | None, ingredient_names: list[str]) -> dict[str, float]:
    """Puntúa (0-1) cada eje de sabor para un producto dado."""
    text = " ".join([name, method or "", *ingredient_names])
    text_n = _normalize(text)
    scores: dict[str, float] = {}
    for axis, keywords in KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text_n)
        bonus = sum(2 for kw in KEYWORD_BONUSES.get(axis, ()) if kw in text_n)
        scores[axis] = round(min(1.0, (hits + bonus) / 3.0), 2)
    return scores


def products_with_profile(
    session: Session, *, continent: str | None = None, category: str | None = None
) -> list[dict]:
    """Productos con su perfil de sabor y continente, aplicando filtros."""
    query = (
        select(models.Product)
        .options(
            selectinload(models.Product.countries),
            selectinload(models.Product.ingredients),
            selectinload(models.Product.categories),
        )
        .where(models.Product.status.in_(["imported", "reviewed"]))
    )
    products = session.execute(query).scalars().all()

    rows = []
    for p in products:
        conts = {c.continent for c in p.countries if c.continent}
        if continent and continent not in conts:
            continue
        cats = {cat.code for cat in p.categories}
        if category and category not in cats:
            continue
        main_continent = sorted(conts)[0] if conts else "Sin dato"
        rows.append(
            {
                "product_id": p.id,
                "name": p.name,
                "continent": main_continent,
                "category": sorted(cats)[0] if cats else None,
                "profile": flavor_profile(
                    p.name,
                    p.method,
                    [i.name for i in p.ingredients],
                ),
            }
        )
    return rows


def aggregate_by_continent(rows: list[dict]) -> list[dict]:
    """Promedia el perfil de sabor por continente."""
    acc: dict[str, list[dict[str, float]]] = {}
    for r in rows:
        acc.setdefault(r["continent"], []).append(r["profile"])
    out = []
    for continent, profiles in sorted(acc.items(), key=lambda kv: -len(kv[1])):
        out.append(
            {
                "continent": continent,
                "products": len(profiles),
                "profile": {
                    axis: round(sum(p[axis] for p in profiles) / len(profiles), 2)
                    for axis in AXES
                },
            }
        )
    return out


_payload_cache: dict[tuple, dict] = {}


def flavor_map_payload(
    session: Session,
    *,
    continent: str | None = None,
    category: str | None = None,
    detail: bool = False,
) -> dict:
    """Payload del mapa de sabores con caché por fingerprint y filtros.

    El escaneo de ~6.000 productos es la operación más cara de la API;
    como la base es estática en producción, se memoiza por fingerprint.
    """
    from app.services.semantic import _dataset_fingerprint

    ing_count = session.execute(
        select(func.count()).select_from(models.Ingredient)
    ).scalar_one()
    key = (_dataset_fingerprint(session), ing_count, continent, category, detail)
    cached = _payload_cache.get(key)
    if cached is not None:
        return cached

    rows = products_with_profile(session, continent=continent, category=category)
    payload = {
        "axes": AXES,
        "continents": aggregate_by_continent(rows),
        "detail": rows if detail else [],
    }
    if len(_payload_cache) > 32:
        _payload_cache.clear()
    _payload_cache[key] = payload
    return payload