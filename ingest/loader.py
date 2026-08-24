from app.db import models
from sqlalchemy.orm import Session

from ingest.categories import CATEGORIES
from ingest.ingredients import pick_substrate
from ingest.normalize import extract_microbes, normalize_name


def seed_categories(session: Session):
    existing = {c.code for c in session.query(models.Category).all()}
    for item in CATEGORIES:
        if item["code"] not in existing:
            session.add(models.Category(**item))
    session.commit()


def seed_country_coords(session: Session):
    """Rellena latitud/longitud de los países desde los centroides por ISO2."""
    from ingest.sources.geo import get_centroid

    updated = 0
    for country in session.query(models.Country).all():
        centroid = get_centroid(country.iso2)
        if centroid and (country.latitude != centroid[0] or country.longitude != centroid[1]):
            country.latitude, country.longitude = centroid
            updated += 1
    session.commit()
    return updated


def _get_or_create_country(session: Session, info: dict) -> models.Country:
    country = session.query(models.Country).filter(
        models.Country.iso2 == info.get("iso2")
    ).first() if info.get("iso2") else None
    if country is None:
        country = session.query(models.Country).filter(
            models.Country.name == info["name"]
        ).first()
    if country is None:
        country = models.Country(
            name=info["name"],
            iso2=info.get("iso2"),
            iso3=info.get("iso3"),
            continent=info.get("continent"),
        )
        session.add(country)
        session.flush()
    return country


def _get_or_create_ingredient(session: Session, info: dict) -> models.Ingredient:
    name = info["name"].strip().lower()
    ingredient = session.query(models.Ingredient).filter(
        models.Ingredient.name == name
    ).first()
    if ingredient is None:
        ingredient = models.Ingredient(name=name, category=info.get("category"))
        session.add(ingredient)
        session.flush()
    return ingredient


def _get_or_create_category(session: Session, code: str) -> models.Category:
    category = session.query(models.Category).filter(
        models.Category.code == code
    ).first()
    if category is None:
        raise ValueError(f"Categoría desconocida: {code}")
    return category


def _get_or_create_microbe(session: Session, name: str) -> models.Microbe:
    name = name.strip()
    microbe = session.query(models.Microbe).filter(
        models.Microbe.name == name
    ).first()
    if microbe is None:
        microbe = models.Microbe(name=name)
        session.add(microbe)
        session.flush()
    return microbe


def _get_or_create_reference(session: Session, info: dict) -> models.Reference:
    url = info.get("url")
    doi = info.get("doi")
    reference = None
    if url:
        reference = session.query(models.Reference).filter(
            models.Reference.url == url
        ).first()
    if reference is None and doi:
        reference = session.query(models.Reference).filter(
            models.Reference.doi == doi
        ).first()
    if reference is None and not url and not doi:
        reference = session.query(models.Reference).filter(
            models.Reference.title == info["title"]
        ).first()
    if reference is None:
        reference = models.Reference(
            title=info["title"],
            ref_type=info.get("ref_type"),
            url=url,
            doi=doi,
        )
        session.add(reference)
        session.flush()
    return reference


def _lookup_by_name(session: Session, name: str) -> models.Product | None:
    # Índice ligado a la sesión (session.info): evita recargar toda la tabla
    # por registro y no contamina entre bases distintas en los tests.
    idx = session.info.setdefault("_name_index", {})
    key = normalize_name(name)
    if not idx:
        idx.update(
            {normalize_name(n): pid for pid, n in session.query(models.Product.id, models.Product.name).all()}
        )
    pid = idx.get(key)
    return session.get(models.Product, pid) if pid else None


def upsert_product(session: Session, record: dict) -> models.Product | None:
    normalized = normalize_name(record["name"])
    product = _lookup_by_name(session, record["name"])
    if product is not None:
        return None
    product = models.Product(
        name=record["name"],
        description=record.get("description"),
        method=record.get("method"),
        fermentation_time=record.get("fermentation_time"),
        status="imported",
        source_tag=record.get("source_tag"),
        substrate=pick_substrate(record.get("ingredients", [])),
        image_url=record.get("image_url"),
    )
    session.add(product)
    session.flush()

    for alias in record.get("aliases", []):
        if normalize_name(alias["name"]) == normalized:
            continue
        product.aliases.append(
            models.ProductAlias(name=alias["name"], language=alias.get("language"))
        )

    for info in record.get("countries", []):
        product.countries.append(_get_or_create_country(session, info))

    for info in record.get("ingredients", []):
        product.ingredients.append(_get_or_create_ingredient(session, info))

    for code in record.get("categories", []):
        product.categories.append(_get_or_create_category(session, code))

    microbe_names = list(record.get("microbes", []))
    if not microbe_names:
        text = " ".join(
            filter(None, [record["name"], record.get("description"), record.get("method")])
        )
        microbe_names = extract_microbes(text)
    for name in microbe_names:
        product.microbes.append(_get_or_create_microbe(session, name))

    for info in record.get("references", []):
        product.references.append(_get_or_create_reference(session, info))

    session.info["_name_index"][normalized] = product.id
    return product


# Productos cuyo nombre es demasiado generico como para considerarlos un
# "ingrediente usado" cuando se menciona en la descripcion de otro producto.
_USE_STOPWORDS = {
    "beer", "wine", "cheese", "yogurt", "yoghurt", "bread", "tea", "vinegar",
    "salt", "sugar", "water", "sauce", "jam", "butter", "cream", "milk",
    "curd", "meat", "fish", "sour cream", "condiment", "condiments", "fruit",
    "fruits", "sausage", "sausages", "fermented fish", "spice", "spices",
    "seasoning", "seasonings", "dish", "dessert", "snack", "drink", "beverage",
    "vegetable", "vegetables", "ingredient", "product", "flour", "grain",
    "grains", "nuts", "pickle", "pickles", "herbs",
}


def enrich_ingredients(session: Session) -> tuple[int, int]:
    """Re-extrae ingredientes sobre los productos ya persistidos (nombre +
    descripcion + metodo) y agrega los que falten, sin duplicar."""
    from ingest.ingredients import match_ingredients, match_ingredients_by_name

    added = 0
    updated_substrate = 0
    for product in session.query(models.Product).filter(
        models.Product.status != "discarded"
    ).all():
        text = " ".join(
            filter(
                None,
                [product.name, product.description, product.method],
            )
        )
        matched = match_ingredients(text)
        if not matched:
            matched = match_ingredients_by_name(product.name)
        if not matched:
            continue
        current = {i.name for i in product.ingredients}
        for info in matched:
            if info["name"] in current:
                continue
            ingredient = _get_or_create_ingredient(session, info)
            product.ingredients.append(ingredient)
            current.add(info["name"])
            added += 1
        new_substrate = pick_substrate(matched)
        if new_substrate and product.substrate is None:
            product.substrate = new_substrate
            updated_substrate += 1
    session.commit()
    return added, updated_substrate


def build_product_uses(session: Session) -> int:
    """Vincula producto->producto cuando el nombre de uno aparece mencionado
    como ingrediente en la descripcion/metodo del otro (sentido 'usar')."""
    import re

    products = session.query(models.Product).all()
    active = [p for p in products if p.status != "discarded"]
    active_ids = {p.id for p in active}
    (
        session.query(models.ProductUse)
        .filter(
            (models.ProductUse.product_id.notin_(active_ids))
            | (models.ProductUse.used_product_id.notin_(active_ids))
        )
        .delete(synchronize_session=False)
    )
    by_name: dict[str, models.Product] = {}
    for product in active:
        key = normalize_name(product.name)
        if len(key) >= 4 and key not in _USE_STOPWORDS and key not in by_name:
            by_name[key] = product
    names = sorted(by_name.keys(), key=len, reverse=True)
    pattern = re.compile(
        r"(?<![a-z0-9])(" + "|".join(re.escape(n) for n in names) + r")(?![a-z0-9])"
    )

    created = 0
    for product in active:
        text = normalize_name(
            " ".join(
                filter(
                    None,
                    [
                        product.description,
                        product.method,
                        " ".join(i.name for i in product.ingredients),
                    ],
                )
            )
        )
        if not text:
            continue
        mentioned = set()
        for m in pattern.finditer(text):
            used = by_name[m.group(1)]
            if used.id != product.id:
                mentioned.add(used.id)
        for used_id in mentioned:
            existing = (
                session.query(models.ProductUse)
                .filter_by(product_id=product.id, used_product_id=used_id)
                .first()
            )
            if existing is None:
                session.add(
                    models.ProductUse(product_id=product.id, used_product_id=used_id)
                )
                created += 1
    session.commit()
    return created


def create_full_text_table():
    from app.db.database import engine
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS products_fts
                USING fts5(name, description, content=products, content_rowid=id)
                """
            )
        )
        conn.execute(text("INSERT INTO products_fts(products_fts) VALUES('rebuild')"))
