"""Tests de microbiota típica por categoría (roadmap 2.2)."""

from ingest.microbiota_profiles import CATEGORY_PROFILES, link_typical_microbiota


def _make_product(session, name, category_code="otro", description=None):
    from app.db import models

    cat = session.query(models.Category).filter(models.Category.code == category_code).first()
    product = models.Product(name=name, status="imported", description=description)
    if cat:
        product.categories.append(cat)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def test_profiles_cover_main_categories():
    for code in ("fermento_lactico", "encurtido_fermentado", "fermento_alcoholico",
                 "fermento_koji", "fermento_alcalino", "fermento_acetico",
                 "fermento_cereal", "curado_sal"):
        assert code in CATEGORY_PROFILES and CATEGORY_PROFILES[code]


def test_links_typical_microbiota(session_factory):
    session = session_factory()
    try:
        from ingest.loader import seed_categories

        seed_categories(session)
        p1 = _make_product(session, "Yogur de prueba", "fermento_lactico")
        p2 = _make_product(
            session, "Cabrales de prueba", "fermento_lactico",
            description="Queso azul asturiano tipo cabrales",
        )
        enriched, links = link_typical_microbiota(session)
        assert enriched >= 2 and links >= 8
        names_p1 = {m.name for m in p1.microbes}
        assert "Lactobacillus plantarum" in names_p1
        # Pista por nombre: Cabrales debe traer Penicillium roqueforti.
        names_p2 = {m.name for m in p2.microbes}
        assert "Penicillium roqueforti" in names_p2
        # Idempotente: segunda pasada no añade nada.
        enriched2, links2 = link_typical_microbiota(session)
        assert enriched2 == 0 and links2 == 0
    finally:
        session.close()


def test_skips_products_without_category_profile(session_factory):
    session = session_factory()
    try:
        from ingest.loader import seed_categories

        seed_categories(session)
        _make_product(session, "Producto sin perfil", "otros")
        enriched, _ = link_typical_microbiota(session)
        assert enriched == 0
    finally:
        session.close()