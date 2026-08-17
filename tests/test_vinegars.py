"""
Tests para Vinagres Caseros, Bebidas Vivas y Filtro por Método.
"""

import sqlite3


def test_vinegars_ingest_integrity():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, method, substrate, image_url FROM products WHERE source_tag = 'vinegar_curated'")
    items = cursor.fetchall()
    conn.close()

    assert len(items) >= 13, "Se esperan al menos 13 productos de vinagres y bebidas vivas"
    for item in items:
        assert item[1] != "", "El nombre del producto no debe estar vacío"
        assert item[2] != "", "El método de fermentación debe estar definido"
        assert item[4] and item[4].startswith("http"), "La imagen debe ser una URL válida"


def test_api_filter_by_method_fermentation(client):
    response = client.get("/products?method=fermentaci%C3%B3n")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0


def test_api_filter_by_method_koji(client):
    response = client.get("/products?method=koji")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
