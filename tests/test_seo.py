"""Tests de SEO y structured data (4.9): sitemap, robots y SSR del detalle."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_sitemap_xml():
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    assert "<urlset" in r.text
    assert "<loc>https://conservas-world.example/p/84</loc>" in r.text
    assert r.text.count("<loc>") > 100


def test_robots_txt():
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert "User-agent: *" in r.text
    assert "Sitemap:" in r.text


def test_product_page_ssr():
    r = client.get("/p/84")
    assert r.status_code == 200
    assert "Burrata" in r.text
    assert "application/ld+json" in r.text
    assert '"@type": "Product"' in r.text
    assert "og:title" in r.text
    assert "twitter:card" in r.text
    assert "canonical" in r.text
    assert "Abrir en la aplicación" in r.text


def test_product_page_404():
    assert client.get("/p/999999").status_code == 404


def test_structured_data_endpoint():
    r = client.get("/.well-known/structured-data")
    assert r.status_code == 200
    products = r.json()["products"]
    assert len(products) > 0
    assert products[0]["@type"] == "Product"
    assert "ingredients" in products[0]


def test_spa_still_served():
    assert client.get("/").status_code == 200