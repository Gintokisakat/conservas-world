from sqlalchemy.orm import Session

from app.db import models
from app.db.database import init_db
from ingest.categories import CATEGORIES
from ingest.normalize import extract_microbes, normalize_name


def seed_categories(session: Session):
    existing = {c.code for c in session.query(models.Category).all()}
    for item in CATEGORIES:
        if item["code"] not in existing:
            session.add(models.Category(**item))
    session.commit()


def _get_or_create_country(session: Session, info: dict) -> models.Country:
    key = info.get("iso2") or normalize_name(info["name"])
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


def upsert_product(session: Session, record: dict) -> models.Product | None:
    normalized = normalize_name(record["name"])
    product = session.query(models.Product).filter(
        models.Product.name == record["name"]
    ).first()
    if product is None:
        product = session.query(models.Product).all()
        product = next((p for p in product if normalize_name(p.name) == normalized), None)
    if product is not None:
        return None
    product = models.Product(
        name=record["name"],
        description=record.get("description"),
        method=record.get("method"),
        fermentation_time=record.get("fermentation_time"),
        status="imported",
        source_tag=record.get("source_tag"),
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

    return product


def create_full_text_table():
    from sqlalchemy import text

    from app.db.database import engine

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
