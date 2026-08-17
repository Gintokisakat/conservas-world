"""Tests de cobertura i18n (4.8): claves ES/EN en sincronía y placeholders traducidos."""

import re

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _extract():
    js = client.get("/static/app.js").text
    es_block = js.split("const i18n = {")[1].split("    en: {")[0]
    en_block = js.split("const i18n = {")[1].split("    en: {")[1].split("};")[0]
    es = set(re.findall(r"^        ([a-z_]+):", es_block, re.M))
    en = set(re.findall(r"^        ([a-z_]+):", en_block, re.M))
    return es, en


def test_es_en_key_sync():
    es, en = _extract()
    assert es == en
    assert len(es) >= 75


def test_html_data_i18n_keys_covered():
    es, en = _extract()
    html = client.get("/").text
    html_keys = set(re.findall(r"data-i18n(?:-placeholder)?=\"([a-z_]+)\"", html))
    assert html_keys - es == set()
    assert html_keys - en == set()


def test_new_placeholder_keys():
    es, en = _extract()
    for key in ["search_placeholder", "ing_placeholder", "prod_placeholder", "glossary_search"]:
        assert key in es and key in en


def test_html_lang_sync():
    js = client.get("/static/app.js").text
    assert "document.documentElement.lang = state.lang" in js


def test_placeholders_applied_dynamically():
    js = client.get("/static/app.js").text
    assert 'querySelectorAll("[data-i18n-placeholder]")' in js
    assert "el.placeholder = t[key]" in js