"""Tests de comportamiento del frontend."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_index_html_loads():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Conservas del Mundo" in resp.text


def test_static_files_serve():
    client = TestClient(app)
    resp = client.get("/static/app.js")
    assert resp.status_code == 200
    assert "function" in resp.text


def test_manifest_json():
    client = TestClient(app)
    resp = client.get("/static/manifest.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data
    assert "short_name" in data


def test_service_worker():
    client = TestClient(app)
    resp = client.get("/static/sw.js")
    assert resp.status_code == 200
    assert "CACHE_NAME" in resp.text


def test_pwa_install_button():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "install-btn" in resp.text


def test_i18n_attributes_present():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "data-i18n" in resp.text


def test_theme_toggle():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "theme-toggle" in resp.text


def test_search_input_present():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "search-input" in resp.text


def test_product_list_container():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "product-list" in resp.text


def test_modal_containers():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "detail" in resp.text
    assert "auth-modal" in resp.text
