"""Tests de productores artesanales (roadmap 4.6) y X-Request-ID (roadmap 5.4)."""



def test_producers_empty(client):
    res = client.get("/producers")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []
    # Test Roadmap 5.4 header X-Request-ID
    assert "x-request-id" in res.headers


def test_create_and_list_producers(client):
    payload = {
        "name": "Fermentos del Valle",
        "country": "Argentina",
        "region": "Mendoza",
        "city": "Uco",
        "address": "Ruta 40 km 80",
        "website": "https://fermentosvalle.example.com",
        "products_offered": "Kéfir de uva, Kombucha silvestre, Chucrut de la huerta",
    }
    create_res = client.post("/producers", json=payload)
    assert create_res.status_code == 201
    prod = create_res.json()
    assert prod["id"] > 0
    assert prod["name"] == "Fermentos del Valle"
    assert prod["country"] == "Argentina"
    assert prod["verified"] is False
    assert "x-request-id" in create_res.headers

    # List with country filter
    list_res = client.get("/producers?country=Argentina")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["name"] == "Fermentos del Valle"

    # Search filter
    search_res = client.get("/producers?q=kombucha")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] == 1


def test_get_single_producer(client):
    payload = {
        "name": "Miso Koji House",
        "country": "Japón",
        "city": "Kyoto",
        "products_offered": "Red Miso, Shio Koji",
    }
    c_res = client.post("/producers", json=payload)
    prod_id = c_res.json()["id"]

    get_res = client.get(f"/producers/{prod_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Miso Koji House"

    not_found = client.get("/producers/999999")
    assert not_found.status_code == 404


def test_update_and_delete_producer_auth(client):
    # Register test user
    reg = client.post(
        "/auth/register",
        json={"email": "producer_owner@example.com", "username": "producerowner", "password": "password123"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create as authenticated user
    payload = {
        "name": "Quesos de Montaña",
        "country": "España",
        "region": "Asturias",
        "city": "Cabrales",
        "products_offered": "Queso Cabrales artesano",
    }
    c_res = client.post("/producers", json=payload, headers=headers)
    assert c_res.status_code == 201
    prod_id = c_res.json()["id"]
    assert c_res.json()["mine"] is True

    # Update
    u_res = client.put(f"/producers/{prod_id}", json={"city": "Arenas de Cabrales"}, headers=headers)
    assert u_res.status_code == 200
    assert u_res.json()["city"] == "Arenas de Cabrales"

    # Delete
    d_res = client.delete(f"/producers/{prod_id}", headers=headers)
    assert d_res.status_code == 200
    assert d_res.json()["status"] == "ok"

    # Verify deleted
    g_res = client.get(f"/producers/{prod_id}")
    assert g_res.status_code == 404

