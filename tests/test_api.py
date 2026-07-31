def test_stats(client):
    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["products"] == 2
    assert data["countries"] == 2
    assert data["by_category"]["fermento_koji"] == 1
    assert data["by_continent"]["Asia"] == 1


def test_list_products(client):
    resp = client.get("/products")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    names = {item["name"] for item in data["items"]}
    assert names == {"Miso", "Sauerkraut"}


def test_filter_by_category(client):
    resp = client.get("/products?category=fermento_koji")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["name"] == "Miso"


def test_filter_by_country(client):
    resp = client.get("/products?country=Germany")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["name"] == "Sauerkraut"


def test_filter_by_country_iso(client):
    resp = client.get("/products?country=jp")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_filter_by_continent(client):
    resp = client.get("/products?continent=Asia")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_search(client):
    resp = client.get("/products?q=col")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["name"] == "Sauerkraut"


def test_pagination(client):
    resp = client.get("/products?page_size=1&page=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1


def test_get_product_detail(client):
    resp = client.get("/products/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Miso"
    assert data["countries"][0]["continent"] == "Asia"
    assert {i["name"] for i in data["ingredients"]} == {"soybean", "rice"}
    assert data["references"][0]["url"] == "https://example.org"


def test_get_product_not_found(client):
    resp = client.get("/products/999")
    assert resp.status_code == 404


def test_random_product(client):
    resp = client.get("/products/random")
    assert resp.status_code == 200
    assert resp.json()["name"] in {"Miso", "Sauerkraut"}


def test_related_products(client):
    resp = client.get("/products/1/related")
    assert resp.status_code == 200
    assert resp.json() == []


def test_related_products_not_found(client):
    resp = client.get("/products/999/related")
    assert resp.status_code == 404


def test_recommendations_make_by_substrate(client):
    resp = client.get("/recommendations?ingredients=cabbage")
    assert resp.status_code == 200
    data = resp.json()
    names = {m["name"] for m in data["make"]}
    assert "Sauerkraut" in names
    sauerkraut = next(m for m in data["make"] if m["name"] == "Sauerkraut")
    assert sauerkraut["substrate"] == "cabbage"
    assert sauerkraut["matched"] == ["cabbage"]
    assert sauerkraut["missing"] == []


def test_recommendations_alias_spanish(client):
    resp = client.get("/recommendations?ingredients=repollo")
    assert resp.status_code == 200
    names = {m["name"] for m in resp.json()["make"]}
    assert "Sauerkraut" in names


def test_recommendations_soybean_matches_miso(client):
    resp = client.get("/recommendations?ingredients=soja,arroz")
    assert resp.status_code == 200
    names = {m["name"] for m in resp.json()["make"]}
    assert "Miso" in names


def test_recommendations_empty(client):
    resp = client.get("/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert data["make"] == []
    assert data["use"] == []


def test_unknown_filter_returns_empty(client):
    resp = client.get("/products?country=Narnia")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_list_categories(client):
    resp = client.get("/categories")
    assert resp.status_code == 200
    assert resp.headers.get("Cache-Control") == "public, max-age=3600"
    codes = {c["code"] for c in resp.json()}
    assert "fermento_lactico" in codes
    assert "encurtido_vinagre" in codes


def test_list_ingredients_cache_header(client):
    resp = client.get("/ingredients")
    assert resp.status_code == 200
    assert resp.headers.get("Cache-Control") == "public, max-age=3600"

