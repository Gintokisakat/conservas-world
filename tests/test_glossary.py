def test_glossary_bilingual_seeded(client):
    resp = client.get("/glossary?lang=es&limit=500")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 100
    terms = {g["term"] for g in data}
    assert "salmuera" in terms
    assert "fermentación" in terms
    resp_en = client.get("/glossary?lang=en&limit=500")
    terms_en = {g["term"] for g in resp_en.json()}
    assert "brine" in terms_en
    assert "fermentation" in terms_en
    assert all(g["language"] == "es" for g in data)
    assert all(g["language"] == "en" for g in resp_en.json())


def test_glossary_search(client):
    resp = client.get("/glossary?lang=es&q=salmuera")
    data = resp.json()
    assert any("salmuera" in g["term"] for g in data)
    assert data[0]["definition"]
    resp_no = client.get("/glossary?lang=es&q=zzzznohit")
    assert resp_no.json() == []


def test_glossary_related_product_linked(client):
    resp = client.get("/glossary?lang=es&product_id=1")
    data = resp.json()
    assert data
    for g in data:
        assert g["related_product_id"] == 1
        assert g["related_product"] is not None
    names = {g["term"] for g in data}
    assert "miso" in names


def test_glossary_in_suggest(client):
    resp = client.get("/search/suggest?q=salmuera")
    data = resp.json()
    types = {s["type"] for s in data["glossary"]}
    assert "glossary" in types
    assert any("salmuera" in s["name"] for s in data["glossary"])
    assert all(s["type"] == "glossary" for s in data["glossary"])


def test_glossary_invalid_lang(client):
    resp = client.get("/glossary?lang=fr")
    assert resp.status_code == 422
