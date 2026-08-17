"""Tests de guías paso a paso (3.4): listado, detalle, i18n y 404."""

from app.main import app
from app.services.guides import GUIDES, get_guide, list_guides
from fastapi.testclient import TestClient

client = TestClient(app)


def test_guides_available_in_code():
    slugs = [g.slug for g in GUIDES]
    assert "kimchi" in slugs
    assert "chucrut" in slugs
    assert "kombucha" in slugs
    assert "miso" in slugs
    assert "yogur" in slugs


def test_list_guides_es():
    items = list_guides("es")
    assert len(items) >= 5
    kimchi = next(g for g in items if g["slug"] == "kimchi")
    assert kimchi["steps"] > 0
    assert "difficulty" in kimchi


def test_list_guides_en():
    items = list_guides("en")
    kimchi = next(g for g in items if g["slug"] == "kimchi")
    assert "cabbage" in kimchi["title"].lower() or "kimchi" in kimchi["title"].lower()


def test_get_guide_detail_es():
    g = get_guide("kimchi", "es")
    assert g is not None
    assert g["steps"][0]["title"] == "Preparar el repollo"
    assert g["steps"][0]["duration_min"] is not None
    assert g["steps"][0]["temp_c"] is not None


def test_get_guide_detail_en():
    g = get_guide("kombucha", "en")
    assert g is not None
    assert "scoby" in g["steps"][1]["body"].lower() or "scoby" in g["steps"][2]["body"].lower()


def test_get_guide_unknown():
    assert get_guide("nope", "es") is None


def test_guide_safety_flag():
    g = get_guide("chucrut", "es")
    assert any(s["safety"] for s in g["steps"])


def test_endpoint_list():
    r = client.get("/guides")
    assert r.status_code == 200
    d = r.json()
    assert len(d) >= 5
    assert d[0]["slug"] in {"kimchi", "chucrut", "kombucha", "miso", "yogur"}


def test_endpoint_detail():
    r = client.get("/guides/kimchi")
    assert r.status_code == 200
    g = r.json()
    assert g["title"] == "Kimchi de repollo"
    assert len(g["steps"]) == 5
    assert g["steps"][0]["temp_c"] == 21


def test_endpoint_detail_404():
    assert client.get("/guides/nope").status_code == 404


def test_endpoint_lang_param():
    r = client.get("/guides/kimchi?lang=en")
    assert r.json()["steps"][0]["title"] == "Prep the cabbage"


def test_guides_in_public_api():
    assert client.get("/api/v1/guides").status_code == 200
    assert client.get("/api/v1/guides/miso").status_code == 200


def test_frontend_has_guide_stepper():
    page = client.get("/").text
    assert 'id="guide-body"' in page
    js = client.get("/static/app.js").text
    assert "renderGuideStep" in js
    assert "guide-timer-btn" in js