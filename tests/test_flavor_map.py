"""Tests del mapa de sabores (3.6): clasificación heurística y endpoint /flavor-map."""

from app.main import app
from app.services.flavors import AXES, aggregate_by_continent, flavor_profile
from fastapi.testclient import TestClient

client = TestClient(app)


def test_flavor_profile_known_product():
    p = flavor_profile("Sauerkraut fermentado", "lacto-fermentación", ["repollo", "sal"])
    assert p["fermentado"] >= 0.67
    assert p["ácido"] >= 0.33
    assert p["salado"] > 0
    assert all(0.0 <= v <= 1.0 for v in p.values())


def test_flavor_profile_spicy():
    p = flavor_profile("Sambal Oelek", "fermentación", ["chile rojo", "sal"])
    assert p["picante"] >= 0.67
    assert p["fermentado"] > 0


def test_flavor_profile_sweet():
    p = flavor_profile("Mermelada de higos con miel", "conserva", ["higos", "miel"])
    assert p["dulce"] >= 0.67


def test_axes_stable():
    assert AXES == ["picante", "ácido", "umami", "dulce", "salado", "amargo", "fermentado"]


def test_aggregate_averages():
    rows = [
        {"continent": "Asia", "profile": {"picante": 0.0, "ácido": 0.0, "umami": 1.0, "dulce": 0.0, "salado": 0.0, "amargo": 0.0, "fermentado": 1.0}},
        {"continent": "Asia", "profile": {"picante": 0.0, "ácido": 0.0, "umami": 1.0, "dulce": 0.0, "salado": 0.0, "amargo": 0.0, "fermentado": 0.0}},
    ]
    out = aggregate_by_continent(rows)
    assert out[0]["continent"] == "Asia"
    assert out[0]["products"] == 2
    assert out[0]["profile"]["umami"] == 1.0
    assert out[0]["profile"]["fermentado"] == 0.5


def test_flavor_map_endpoint():
    r = client.get("/flavor-map")
    assert r.status_code == 200
    d = r.json()
    assert set(d["axes"]) == set(AXES)
    assert len(d["continents"]) > 0
    for c in d["continents"]:
        assert set(c["profile"]) == set(AXES)
        assert c["products"] > 0


def test_flavor_map_filter_by_continent():
    r = client.get("/flavor-map?continent=Asia")
    d = r.json()
    names = {c["continent"] for c in d["continents"]}
    assert "Asia" in names
    assert all(c["products"] > 0 for c in d["continents"])


def test_flavor_map_detail():
    r = client.get("/flavor-map?detail=1&continent=Asia")
    d = r.json()
    assert len(d["detail"]) > 0
    assert d["detail"][0]["profile"]["umami"] >= 0.0


def test_flavor_map_available_in_public_api():
    assert client.get("/api/v1/flavor-map").status_code == 200