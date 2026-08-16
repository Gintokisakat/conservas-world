import pytest


@pytest.fixture()
def cheese_session(session_factory):
    from ingest.loader import seed_categories, upsert_product

    session = session_factory()
    seed_categories(session)
    records = [
        {
            "name": "Cheddar",
            "description": "Queso inglés.",
            "method": None,
            "fermentation_time": None,
            "aliases": [],
            "countries": [],
            "ingredients": [{"name": "milk", "category": "lacteo"}],
            "categories": ["fermento_lactico"],
            "references": [],
            "source_tag": "test",
        },
        {
            "name": "Grana Padano",
            "description": "Queso italiano de pasta dura.",
            "method": None,
            "fermentation_time": None,
            "aliases": [],
            "countries": [],
            "ingredients": [{"name": "milk", "category": "lacteo"}],
            "categories": ["fermento_lactico"],
            "references": [],
            "source_tag": "test",
        },
        {
            "name": "Goudale",
            "description": "Cerveza belga.",
            "method": "fermentación",
            "fermentation_time": None,
            "aliases": [],
            "countries": [],
            "ingredients": [{"name": "barley", "category": "cereal"}],
            "categories": ["fermento_alcoholico"],
            "references": [],
            "source_tag": "test",
        },
    ]
    for record in records:
        upsert_product(session, record)
    session.commit()
    yield session
    session.close()


def test_metacheese_parser_rows():
    from ingest.sources.metacheese import _NUMERIC_META, _load_table, _taxa_columns

    table = _load_table()
    assert len(table["Subtype"]) == 1593
    assert "Lactococcus_lactis" in table
    taxa = _taxa_columns(list(table.keys()))
    for col in _NUMERIC_META:
        assert col not in taxa


def test_metacheese_subtypes_with_taxa():
    from ingest.sources.metacheese import _subtypes_with_taxa

    data = _subtypes_with_taxa()
    assert len(data) == 156
    cheddar = data["Cheddar"]
    assert cheddar["sample_count"] == 104
    lactis = next(t for t in cheddar["taxa"] if t["name"] == "Lactococcus lactis")
    assert lactis["mean_abundance"] > 30
    assert lactis["prevalence"] >= 0.5
    blue = data["Blue_cheese"]
    assert any(t["name"] == "Penicillium roqueforti" for t in blue["taxa"])


def test_metacheese_match_exact(cheese_session):
    from app.db import models
    from ingest.sources.metacheese import _match_subtype_to_products
    from sqlalchemy import select

    products = cheese_session.execute(select(models.Product)).scalars().all()
    hits = _match_subtype_to_products("Cheddar", products)
    assert [p.name for p in hits] == ["Cheddar"]


def test_metacheese_match_curated_alias(cheese_session):
    from app.db import models
    from ingest.sources.metacheese import _match_subtype_to_products
    from sqlalchemy import select

    products = cheese_session.execute(select(models.Product)).scalars().all()
    grana = _match_subtype_to_products("Grana", products)
    assert [p.name for p in grana] == ["Grana Padano"]


def test_metacheese_match_no_false_positive(cheese_session):
    """Goudale no debe casar con Gouda ni Blue_cheese (límites de palabra)."""
    from app.db import models
    from ingest.sources.metacheese import _match_subtype_to_products
    from sqlalchemy import select

    products = cheese_session.execute(select(models.Product)).scalars().all()
    assert _match_subtype_to_products("Noord_Hollandse_Gouda", products) == []
    assert _match_subtype_to_products("Blue_cheese", products) == []


def test_metacheese_populate(cheese_session):
    from app.db import models
    from ingest.sources.metacheese import populate_metacheese
    from sqlalchemy import select

    updated = populate_metacheese(cheese_session)
    rows = cheese_session.execute(select(models.CheeseMetagenome)).scalars().all()
    names = {}
    for r in rows:
        product = cheese_session.get(models.Product, r.product_id)
        names[product.name] = r
    assert "Cheddar" in names
    assert names["Cheddar"].subtype == "Cheddar"
    assert names["Cheddar"].sample_count == 104
    assert "Grana Padano" in names
    assert names["Grana Padano"].subtype == "Grana"
    assert "Goudale" not in names
    assert updated >= 2


def test_api_product_metagenome(client, cheese_session):
    from app.db import models
    from ingest.sources.metacheese import populate_metacheese
    from sqlalchemy import select

    populate_metacheese(cheese_session)
    product = cheese_session.execute(
        select(models.Product).where(models.Product.name == "Cheddar")
    ).scalar_one()
    resp = client.get(f"/products/{product.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["metagenome"] is not None
    assert data["metagenome"]["subtype"] == "Cheddar"
    assert data["metagenome"]["sample_count"] == 104
    assert data["metagenome"]["taxa"]
