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


def test_filter_by_fermentation_time(client):
    resp = client.get("/products?fermentation_time=weeks")
    assert resp.status_code == 200


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


def test_list_microbes(client):
    resp = client.get("/microbes")
    assert resp.status_code == 200
    assert resp.headers.get("Cache-Control") == "public, max-age=3600"


def test_get_product_detail_lang_en(client):
    resp = client.get("/products/2?lang=en")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Sauerkraut"


def test_filter_by_source(client):
    resp = client.get("/products?source=test")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_filter_by_source_no_match(client):
    resp = client.get("/products?source=nonexistent")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_filter_by_ingredient(client):
    resp = client.get("/products?ingredient=soybean")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["name"] == "Miso"


def test_filter_by_ingredient_no_match(client):
    resp = client.get("/products?ingredient=chocolate")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_list_references(client):
    resp = client.get("/references")
    assert resp.status_code == 200
    assert resp.headers.get("Cache-Control") == "public, max-age=3600"
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Test reference"


def test_search_by_alias(client):
    resp = client.get("/products?q=col fermentada")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["name"] == "Sauerkraut"


def test_recommendations_use_product(client):
    resp = client.get("/recommendations?products=miso")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["make"]) == 0
    assert len(data["use"]) == 0


def test_product_detail_has_aliases(client):
    resp = client.get("/products/2")
    assert resp.status_code == 200
    data = resp.json()
    alias_names = [a["name"] for a in data["aliases"]]
    assert "chucrut" in alias_names


def test_product_detail_has_ingredients(client):
    resp = client.get("/products/1")
    assert resp.status_code == 200
    data = resp.json()
    ing_names = {i["name"] for i in data["ingredients"]}
    assert ing_names == {"soybean", "rice"}


def test_product_detail_has_microbes(client):
    resp = client.get("/products/1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["microbes"], list)


def test_product_detail_has_diet_tags(client):
    resp = client.get("/products/1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["diet_tags"], list)
    assert "vegan" in data["diet_tags"]
    assert "soy_free" not in data["diet_tags"]


def test_list_products_has_diet_tags(client):
    resp = client.get("/products")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all("diet_tags" in item for item in items)


def test_filter_by_diet_vegan(client):
    resp = client.get("/products?diet=vegan")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_filter_by_diet_spicy(client):
    resp = client.get("/products?diet=spicy")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_filter_by_diet_invalid(client):
    resp = client.get("/products?diet=malarkey")
    assert resp.status_code == 400


def test_list_diets(client):
    resp = client.get("/diets")
    assert resp.status_code == 200
    assert resp.headers.get("Cache-Control") == "public, max-age=3600"
    tags = resp.json()
    assert "vegan" in tags
    assert "spicy" in tags


def test_random_product_always_returns_one(client):
    for _ in range(5):
        resp = client.get("/products/random")
        assert resp.status_code == 200
        assert resp.json()["name"] in {"Miso", "Sauerkraut"}


def test_related_products_with_shared_categories(client):
    resp = client.get("/products/1/related")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_stats_has_all_fields(client):
    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "products" in data
    assert "countries" in data
    assert "ingredients" in data
    assert "categories" in data
    assert "references" in data
    assert "microbes" in data
    assert "products_with_ingredients" in data
    assert "products_with_substrate" in data
    assert "uses" in data
    assert "by_category" in data
    assert "by_continent" in data
    assert "by_source" in data


def test_seasonal_default_month(client):
    resp = client.get("/seasonal")
    assert resp.status_code == 200
    data = resp.json()
    assert 1 <= data["month"] <= 12
    assert data["month_name"]["es"]
    assert data["month_name"]["en"]
    assert resp.headers.get("Cache-Control") == "public, max-age=86400"


def test_seasonal_cabbage_month_includes_sauerkraut(client):
    resp = client.get("/seasonal?month=1")
    assert resp.status_code == 200
    data = resp.json()
    names = [i["name"] for i in data["ingredients"]]
    assert "cabbage" in names
    assert any(p["name"] == "Sauerkraut" for p in data["products"])


def test_seasonal_cabbage_out_of_season(client):
    resp = client.get("/seasonal?month=7")
    assert resp.status_code == 200
    data = resp.json()
    assert "cabbage" not in [i["name"] for i in data["ingredients"]]
    assert data["total"] == 0
    assert data["products"] == []


def test_seasonal_filter_by_continent(client):
    resp = client.get("/seasonal?month=1&continent=Europe")
    data = resp.json()
    assert any(p["name"] == "Sauerkraut" for p in data["products"])
    resp = client.get("/seasonal?month=1&continent=Asia")
    data = resp.json()
    assert all(p["name"] != "Sauerkraut" for p in data["products"])


def test_seasonal_invalid_month(client):
    assert client.get("/seasonal?month=0").status_code == 422
    assert client.get("/seasonal?month=13").status_code == 422


def test_seasonal_data_file_structure():
    """data/seasonal.json con estructura válida (meses 1-12) y nombres usables."""
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "seasonal.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "ingredients" in data and data["ingredients"]
    for name, months in data["ingredients"].items():
        assert name.strip()
        assert months and all(isinstance(m, int) and 1 <= m <= 12 for m in months), name
    # el contrato del endpoint: los nombres deben existir entre los canónicos
    known = {"apple", "cabbage", "bean", "carrot", "corn", "rice", "soybean", "cucumber"}
    assert known & set(data["ingredients"].keys())
    # curado de prueba: el hueco detectado (nombre no canónico) no debe reaparecer
    assert "mulberry" not in data["ingredients"]


