"""Tests de cervecerías y sidrerías artesanales (roadmap 2.7)."""

from ingest.sources.openbrewery import seed_breweries


def test_breweries_seed_and_list(client, session_factory):
    # Seed sample breweries
    session = session_factory()
    try:
        count = seed_breweries(session)
        assert count >= 5
    finally:
        session.close()

    res = client.get("/breweries")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 5
    assert len(data["items"]) >= 5

    # Filter by country
    arg_res = client.get("/breweries?country=Argentina")
    assert arg_res.status_code == 200
    arg_data = arg_res.json()
    assert arg_data["total"] >= 1
    assert any(b["name"] == "Cervecería Antares" for b in arg_data["items"])

    # Filter by type
    cidery_res = client.get("/breweries?by_type=cidery")
    assert cidery_res.status_code == 200
    cidery_data = cidery_res.json()
    assert cidery_data["total"] >= 1
    assert any(b["brewery_type"] == "cidery" for b in cidery_data["items"])


def test_get_brewery_detail(client, session_factory):
    session = session_factory()
    try:
        seed_breweries(session)
    finally:
        session.close()

    list_res = client.get("/breweries?country=Argentina")
    brewery_id = list_res.json()["items"][0]["id"]

    detail_res = client.get(f"/breweries/{brewery_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["name"] == "Cervecería Antares"

    not_found = client.get("/breweries/999999")
    assert not_found.status_code == 404
