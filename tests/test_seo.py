"""Tests de SEO y structured data (4.9): sitemap, robots y SSR del detalle."""

from app.api.seo import SITE_URL
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_site_url_real():
    assert SITE_URL.endswith("conservas-del-mundo.onrender.com")
    assert "example" not in SITE_URL


def test_sitemap_xml():
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    assert "<urlset" in r.text
    assert "<loc>https://conservas-del-mundo.onrender.com/p/84</loc>" in r.text
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


def test_index_homepage_og_meta():
    r = client.get("/")
    assert "og:type" in r.text
    assert "og:title" in r.text
    assert "og:image" in r.text
    assert "twitter:card" in r.text
    assert 'application/ld+json' in r.text
    assert "SearchAction" in r.text
    assert SITE_URL in r.text


def test_og_default_image_existe():
    r = client.get("/static/img/og-default.png")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image")