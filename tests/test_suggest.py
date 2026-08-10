def test_suggest_empty_query(client):
    resp = client.get("/search/suggest", params={"q": " "})
    assert resp.status_code == 200
    assert resp.json() == {"products": [], "ingredients": []}


def test_suggest_product_prefix(client):
    resp = client.get("/search/suggest", params={"q": "mis"})
    assert resp.status_code == 200
    data = resp.json()
    names = [p["name"] for p in data["products"]]
    assert "Miso" in names
    miso = next(p for p in data["products"] if p["name"] == "Miso")
    assert miso["type"] == "product"
    assert miso["id"] == 1
    assert miso["category"] == "Fermento con hongos (koji/moho)"
    assert miso["country"] == "Japan"


def test_suggest_ingredient_prefix(client):
    resp = client.get("/search/suggest", params={"q": "cabb"})
    data = resp.json()
    names = [i["name"] for i in data["ingredients"]]
    assert "cabbage" in names
    cabbage = next(i for i in data["ingredients"] if i["name"] == "cabbage")
    assert cabbage["type"] == "ingredient"
    assert cabbage["category"] == "vegetal"


def test_suggest_ingredient_contains_fallback(client):
    resp = client.get("/search/suggest", params={"q": "bean"})
    data = resp.json()
    names = [i["name"] for i in data["ingredients"]]
    assert "soybean" in names


def test_suggest_limits(client):
    resp = client.get("/search/suggest", params={"q": "a", "limit": 3})
    data = resp.json()
    assert len(data["products"]) <= 3
    assert len(data["ingredients"]) <= 3
