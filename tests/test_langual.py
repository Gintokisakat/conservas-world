"""Tests de la faceta LanguaL (2.16): endpoint de vocabulario y mapeo de categorías."""

import pytest
from app.langual import _LANGUAL_TERMS, CATEGORY_LANGUAL
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _get(lang="es"):
    resp = client.get(f"/api/v1/langual?lang={lang}")
    assert resp.status_code == 200, resp.text
    return resp, resp.json()


def test_langual_endpoint_shape_es():
    resp, data = _get("es")
    assert resp.headers["Cache-Control"] == "public, max-age=86400"
    assert len(data["terms"]) >= 15
    assert len(data["categories"]) == len(CATEGORY_LANGUAL)
    for tm in data["terms"]:
        assert tm["facet"] in ("A", "H", "J")
        assert tm["code"]
        assert tm["label"]
    fermento = next(c for c in data["categories"] if c["code"] == "fermento_lactico")
    assert fermento["langual"] == ["H0101", "J0104"]
    assert fermento["products"] > 0
    assert data["total_products"] == sum(c["products"] for c in data["categories"])


def test_langual_endpoint_en():
    _, data_es = _get("es")
    _, data_en = _get("en")
    labels_es = {t["code"]: t["label"] for t in data_es["terms"]}
    labels_en = {t["code"]: t["label"] for t in data_en["terms"]}
    assert labels_es["H0101"] != labels_en["H0101"]
    assert "lactic acid" in labels_en["H0101"].lower()
    cat_es = {c["code"]: c["name"] for c in data_es["categories"]}
    cat_en = {c["code"]: c["name"] for c in data_en["categories"]}
    assert cat_es["fermento_lactico"] != cat_en["fermento_lactico"]
    # Los códigos (vocabulario controlado) no cambian entre idiomas
    assert set(labels_es) == set(labels_en)


def test_all_db_categories_map_to_langual():
    rows = client.get("/api/v1/categories").json()
    db_codes = {c["code"] for c in rows}
    assert len(db_codes) == len(CATEGORY_LANGUAL)
    assert set(CATEGORY_LANGUAL) == db_codes


def test_langual_referenced_codes_are_defined():
    referenced = set()
    for codes in CATEGORY_LANGUAL.values():
        referenced.update(codes)
    assert referenced, "debe haber código LanguaL mapeado"
    unknowns = referenced - set(_LANGUAL_TERMS)
    assert not unknowns, f"códigos LanguaL sin descriptor: {unknowns}"


def test_langual_categories_products_consistent():
    _, data = _get("es")
    assert data["total_products"] >= 0
    assert all(c["products"] >= 0 for c in data["categories"])


@pytest.mark.parametrize(
    "code, facet",
    [
        ("H0101", "LACTIC"),
        ("H0300", "ACETIC"),
        ("H0232", "ALCOHOL"),
        ("J0104", "FERMENTATION"),
    ],
)
def test_langual_key_descriptors_present(code, facet):
    assert code in _LANGUAL_TERMS
    assert facet.lower().replace(" ", "_") in _LANGUAL_TERMS[code].label_en.lower()