"""Tests de seguridad predictiva (2.3): clasificación por tipo de fermento y endpoint /safety."""

from app.main import app
from app.services.safety import classify, safety_assessment
from fastapi.testclient import TestClient

client = TestClient(app)


def test_classify_koji():
    p = type("P", (), {"name": "Miso japonés", "method": "fermentación con koji", "dairy": None, "metagenome": None})()
    assert classify(p).key == "koji"


def test_classify_acetic():
    p = type("P", (), {"name": "Vinagre de manzana", "method": "fermentación acética", "dairy": None, "metagenome": None})()
    assert classify(p).key == "acetic"


def test_classify_dairy_by_keyword():
    p = type("P", (), {"name": "Queso manchego", "method": None, "dairy": None, "metagenome": None})()
    assert classify(p).key == "dairy"


def test_classify_dairy_by_relation():
    p = type("P", (), {"name": "Burrata", "method": None, "dairy": object(), "metagenome": None})()
    assert classify(p).key == "dairy"


def test_classify_cured():
    p = type("P", (), {"name": "Jamón serrano curado", "method": "salazón", "dairy": None, "metagenome": None})()
    assert classify(p).key == "cured"


def test_assessment_ph_and_alerts():
    p = type("P", (), {"id": 1, "name": "Kimchi", "method": "lacto", "dairy": None, "metagenome": None})()
    a = safety_assessment(p, "es")
    assert a["ph_min"] <= a["ph_max"]
    assert a["risk"] in {"bajo", "medio", "alto"}
    assert a["alerts"]
    assert a["ph_requirement"]


def test_assessment_lang():
    p = type("P", (), {"id": 1, "name": "Miso", "method": "koji", "dairy": None, "metagenome": None})()
    assert "salt" in safety_assessment(p, "en")["alerts"][0].lower() or "botulism" in safety_assessment(p, "en")["alerts"][0].lower()


def test_endpoint_returns_safety():
    r = client.get("/products/3958/safety")
    assert r.status_code == 200
    d = r.json()
    assert d["ph_min"] >= 0
    assert d["category"]
    assert d["risk"] in {"bajo", "medio", "alto"}
    assert "alerts" in d


def test_endpoint_404():
    assert client.get("/products/999999/safety").status_code == 404


def test_endpoint_lang_en():
    d = client.get("/products/3958/safety?lang=en").json()
    assert d["category"] in {"Fermented dairy", "Soy/koji ferments", "Lacto-fermented vegetables", "Cured and salted", "Pickles and vinegars", "Fermented beverages", "Generic ferment"}


def test_safety_in_public_api():
    assert client.get("/api/v1/products/3958/safety").status_code == 200


def test_frontend_has_safety_block():
    js = client.get("/static/app.js").text
    assert "safetyHtml" in js
    assert "/safety?lang=" in js