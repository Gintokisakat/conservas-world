def test_geo_returns_points(client):
    resp = client.get("/products/geo?limit=500")
    assert resp.status_code == 200
    data = resp.json()
    assert data
    miso = [p for p in data if p["name"] == "Miso"]
    assert miso
    jp = next(p for p in miso if p["country"] == "Japan")
    assert abs(jp["lat"] - 36.204824) < 0.1
    assert abs(jp["lng"] - 138.252924) < 0.1
    assert jp["id"] == 1
    assert all("lat" in p and "lng" in p for p in data)


def test_geo_continent_filter(client):
    resp = client.get("/products/geo?continent=Asia&limit=500")
    data = resp.json()
    assert data
    assert all(p["continent"] == "Asia" for p in data)
    names = {p["name"] for p in data}
    assert "Miso" in names
    assert "Sauerkraut" not in names


def test_geo_query_filter(client):
    resp = client.get("/products/geo?q=miso&limit=500")
    data = resp.json()
    assert any(p["name"] == "Miso" for p in data)


def test_geo_limit_boundary(client):
    resp = client.get("/products/geo?limit=20000")
    assert resp.status_code == 200
    resp_bad = client.get("/products/geo?limit=0")
    assert resp_bad.status_code == 422


def test_geo_country_filter(client):
    resp = client.get("/products/geo?country=JP&limit=500")
    data = resp.json()
    assert data
    assert all(p["country"] == "Japan" for p in data)
