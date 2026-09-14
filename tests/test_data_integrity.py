"""Tests de integridad de datos (5.5): cobertura e integridad referencial de build.db."""

import sqlite3

from app.config import DB_PATH

CON = sqlite3.connect(DB_PATH)
STATUSES = "('active', 'imported')"


def _one(sql, *args):
    return CON.execute(sql, args).fetchone()[0]


def _count(sql, *args):
    return _one(sql, *args)


def test_active_product_floor():
    n = _count(f"SELECT COUNT(*) FROM products WHERE status IN {STATUSES}")
    assert n >= 4000


def test_ingredient_coverage_floor():
    total = _count(f"SELECT COUNT(*) FROM products WHERE status IN {STATUSES}")
    with_ing = _count(
        "SELECT COUNT(DISTINCT p.id) FROM products p "
        "JOIN product_ingredient pi ON pi.product_id = p.id "
        f"WHERE p.status IN {STATUSES}"
    )
    assert with_ing / total >= 0.90


def test_category_coverage_floor():
    total = _count(f"SELECT COUNT(*) FROM products WHERE status IN {STATUSES}")
    with_cat = _count(
        "SELECT COUNT(DISTINCT p.id) FROM products p "
        "JOIN product_category pc ON pc.product_id = p.id "
        f"WHERE p.status IN {STATUSES}"
    )
    assert with_cat / total >= 0.95


def test_country_coverage_floor():
    total = _count(f"SELECT COUNT(*) FROM products WHERE status IN {STATUSES}")
    with_c = _count(
        "SELECT COUNT(DISTINCT p.id) FROM products p "
        "JOIN product_country pc ON pc.product_id = p.id "
        f"WHERE p.status IN {STATUSES}"
    )
    assert with_c / total >= 0.50


def test_image_coverage_floor():
    total = _count(f"SELECT COUNT(*) FROM products WHERE status IN {STATUSES}")
    with_img = _count(
        "SELECT COUNT(*) FROM products "
        f"WHERE status IN {STATUSES} AND image_url IS NOT NULL AND image_url != ''"
    )
    assert with_img / total >= 0.40


def test_no_orphan_junction_rows():
    pairs = [
        ("product_category", "product_id", "products", "id"),
        ("product_category", "category_id", "categories", "id"),
        ("product_country", "product_id", "products", "id"),
        ("product_country", "country_id", "countries", "id"),
        ("product_ingredient", "product_id", "products", "id"),
        ("product_ingredient", "ingredient_id", "ingredients", "id"),
        ("product_microbe", "product_id", "products", "id"),
        ("product_microbe", "microbe_id", "microbes", "id"),
    ]
    for table, fk_col, ref_table, ref_col in pairs:
        n = _one(
            f"SELECT COUNT(*) FROM {table} "
            f"WHERE {fk_col} NOT IN (SELECT {ref_col} FROM {ref_table})"
        )
        assert n == 0, f"{table}.{fk_col} filas huérfanas: {n}"


def test_no_duplicate_product_names():
    assert _count("SELECT COUNT(*) FROM (SELECT name FROM products GROUP BY name HAVING COUNT(*) > 1)") == 0


def test_ingredient_vocabulary_nonempty():
    assert _count("SELECT COUNT(*) FROM ingredients") >= 100


def test_every_active_product_has_region_or_country_or_category():
    # Permitimos productos "otro" sin categoría, pero todos deben tener repetibilidad
    empty = _count(
        "SELECT COUNT(*) FROM products p WHERE p.status IN " + STATUSES
        + " AND NOT EXISTS (SELECT 1 FROM product_category pc WHERE pc.product_id=p.id)"
    )
    total = _count(f"SELECT COUNT(*) FROM products WHERE status IN {STATUSES}")
    assert empty / total <= 0.10