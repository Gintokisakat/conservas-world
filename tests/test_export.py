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
