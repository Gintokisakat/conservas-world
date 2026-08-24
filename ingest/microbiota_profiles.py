"""Microbiota típica por categoría de fermento (roadmap 2.2).

Para productos sin ningún microbio vinculado, asocia la microbiota
característica de su categoría (y pistas por nombre), igual que MetaCheeseDB
hace para quesos pero generalizado. Es microbiota TÍPICA del tipo de
fermento, no un aislado documentado producto por producto.
"""

from app.db import models
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ingest.loader import _get_or_create_microbe
from ingest.normalize import normalize_name

# Perfiles base por categoría (nombres que existen o se crearán en microbes).
CATEGORY_PROFILES: dict[str, list[str]] = {
    "fermento_lactico": [
        "Lactobacillus plantarum",
        "Streptococcus thermophilus",
        "Lactococcus lactis",
        "Leuconostoc mesenteroides",
        "Lactobacillus bulgaricus",
        "Lactobacillus helveticus",
    ],
    "encurtido_fermentado": [
        "Lactobacillus plantarum",
        "Leuconostoc mesenteroides",
    ],
    "encurtido_salmuera": [
        "Leuconostoc mesenteroides",
        "Lactobacillus plantarum",
    ],
    "encurtido_vinagre": [
        "Lactobacillus plantarum",
    ],
    "fermento_alcoholico": [
        "Saccharomyces cerevisiae",
    ],
    "fermento_acetico": [
        "Acetobacter aceti",
        "Komagataeibacter xylinus",
    ],
    "fermento_koji": [
        "Aspergillus oryzae",
        "Rhizopus oryzae",
    ],
    "fermento_alcalino": [
        "Bacillus subtilis",
    ],
    "fermento_cereal": [
        "Lactobacillus plantarum",
        "Saccharomyces cerevisiae",
    ],
    "curado_sal": [
        "Staphylococcus equorum",
        "Micrococcus luteus",
    ],
}

# Pistas por nombre -> microbio adicional específico
NAME_HINTS: list[tuple[str, str]] = [
    ("roquefort", "Penicillium roqueforti"),
    ("gorgonzola", "Penicillium roqueforti"),
    ("cabrales", "Penicillium roqueforti"),
    ("stilton", "Penicillium roqueforti"),
    ("danablu", "Penicillium roqueforti"),
    ("camembert", "Penicillium camemberti"),
    ("brie", "Penicillium camemberti"),
    ("tempeh", "Rhizopus oligosporus"),
    ("natto", "Bacillus subtilis"),
    ("ang-khak", "Monascus purpureus"),
    ("red yeast", "Monascus purpureus"),
]


def _existing_microbe_ids(session: Session) -> dict[str, int]:
    return {
        normalize_name(m.name): m.id
        for m in session.execute(select(models.Microbe)).scalars()
    }


def link_typical_microbiota(session: Session) -> tuple[int, int]:
    """Vincula microbiota típica a productos activos sin microbios.

    Devuelve (productos_enriquecidos, vínculos_creados).
    """
    products = session.execute(
        select(models.Product)
        .where(models.Product.status != "discarded")
        .options()  # carga simple; product_microbe se consulta aparte
    ).scalars().all()

    linked_counts = dict(
        session.execute(
            select(models.product_microbe.c.product_id, func.count())
            .group_by(models.product_microbe.c.product_id)
        ).all()
    )

    enriched = 0
    created_links = 0
    for product in products:
        if linked_counts.get(product.id, 0) > 0:
            continue
        categories = {c.code for c in product.categories}
        taxa: list[str] = []
        for code in categories:
            taxa.extend(CATEGORY_PROFILES.get(code, []))
        haystack = f"{product.name} {product.description or ''}".lower()
        for needle, microbe in NAME_HINTS:
            if needle in haystack:
                taxa.append(microbe)
        if not taxa:
            continue

        cache = _existing_microbe_ids(session)
        added_any = False
        seen_ids: set[int] = set()
        for taxon in dict.fromkeys(taxa):  # dedupe preservando orden
            key = normalize_name(taxon)
            mid = cache.get(key)
            if mid is None:
                microbe = _get_or_create_microbe(session, taxon)
                session.flush()
                cache[key] = microbe.id
                mid = microbe.id
            if mid in seen_ids:
                continue
            exists = session.execute(
                select(models.product_microbe.c.microbe_id).where(
                    models.product_microbe.c.product_id == product.id,
                    models.product_microbe.c.microbe_id == mid,
                )
            ).first()
            if exists:
                continue
            session.execute(
                models.product_microbe.insert().values(product_id=product.id, microbe_id=mid)
            )
            seen_ids.add(mid)
            created_links += 1
            added_any = True
        if added_any:
            enriched += 1
    session.commit()
    return enriched, created_links