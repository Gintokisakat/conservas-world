def test_export_csv(client):
    resp = client.get("/products/1/export?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "attachment" in resp.headers["content-disposition"]
    assert "filename=\"producto-1.csv\"" in resp.headers["content-disposition"]
    text = resp.content.decode("utf-8-sig")
    assert "Nombre" in text
    assert "Miso" in text
    assert "soybean" in text
    assert "rice" in text


def test_export_csv_english(client):
    resp = client.get("/products/1/export?format=csv&lang=en")
    text = resp.content.decode("utf-8-sig")
    assert "Name" in text
    assert "Fermentation time" in text


def test_export_pdf_printable_html(client):
    resp = client.get("/products/1/export?format=pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "Miso" in resp.text
    assert "window.print" in resp.text
    assert "Ingredientes clave" in resp.text
    assert "<!DOCTYPE html>" in resp.text


def test_export_pdf_english(client):
    resp = client.get("/products/1/export?format=pdf&lang=en")
    assert "Key Ingredients" in resp.text


def test_export_invalid_format(client):
    resp = client.get("/products/1/export?format=exe")
    assert resp.status_code == 422


def test_export_not_found(client):
    resp = client.get("/products/99999/export?format=csv")
    assert resp.status_code == 404


def test_export_csv_incluye_imagen(client, db_session):
    from app.db import models
    from sqlalchemy import select

    product = db_session.scalar(select(models.Product).where(models.Product.name == "Miso"))
    product.image_url = "https://example.org/miso.jpg"
    db_session.commit()

    resp = client.get("/products/1/export?format=csv")
    text = resp.content.decode("utf-8-sig")
    assert "Imagen" in text
    assert "https://example.org/miso.jpg" in text


def test_export_csv_sin_imagen_campo_vacio(client):
    resp = client.get("/products/2/export?format=csv")
    text = resp.content.decode("utf-8-sig")
    assert "Imagen" in text


def test_export_pdf_incluye_img(client, db_session):
    from app.db import models
    from sqlalchemy import select

    product = db_session.scalar(select(models.Product).where(models.Product.name == "Miso"))
    product.image_url = "https://example.org/miso.jpg"
    db_session.commit()

    resp = client.get("/products/1/export?format=pdf")
    assert 'src="https://example.org/miso.jpg"' in resp.text
    assert 'class="hero"' in resp.text


def test_export_pdf_sin_imagen_omite_img(client):
    resp = client.get("/products/2/export?format=pdf")
    assert "<img" not in resp.text
    assert 'class="hero"' in resp.text
