"""Tests de restauración de BD desde release (validación, sin red)."""

import sqlite3

from ingest.restore import MIN_PRODUCTS, validate_db


def _make_db(path, products: int):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT)")
    conn.executemany(
        "INSERT INTO products (name) VALUES (?)", [(f"p{i}",) for i in range(products)]
    )
    conn.commit()
    conn.close()


def test_validate_ok(tmp_path):
    db = tmp_path / "ok.db"
    _make_db(db, MIN_PRODUCTS + 1)
    ok, detail = validate_db(db)
    assert ok and str(MIN_PRODUCTS + 1) in detail


def test_validate_too_small(tmp_path):
    db = tmp_path / "small.db"
    _make_db(db, 3)
    ok, detail = validate_db(db)
    assert not ok and "incompleta" in detail.lower()


def test_validate_corrupt(tmp_path):
    db = tmp_path / "corrupt.db"
    db.write_bytes(b"no es una base de datos")
    ok, detail = validate_db(db)
    assert not ok and "inv" in detail.lower()