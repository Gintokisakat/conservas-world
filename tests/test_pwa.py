"""Tests de PWA (4.7): manifest, iconos, service worker y botón de instalación."""

import json

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_manifest_served():
    r = client.get("/static/manifest.json")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    m = r.json()
    assert m["id"] == "/"
    assert m["display"] == "standalone"
    assert m["name"] == "Conservas del Mundo"
    assert m["start_url"] == "/"
    assert m["theme_color"] == "#2d5a3f"


def test_manifest_icons():
    m = json.loads(client.get("/static/manifest.json").text)
    purposes = {i["purpose"] for i in m["icons"]}
    assert "maskable" in purposes
    for icon in m["icons"]:
        path = icon["src"].lstrip("/")
        assert client.get(f"/{path}").status_code == 200, path


def test_sw_served_and_versioned():
    r = client.get("/static/sw.js")
    assert r.status_code == 200
    text = r.text
    assert "self.addEventListener(\"install\"" in text
    assert "icon-maskable.svg" in text


def test_sw_serves_offline_shell():
    r = client.get("/static/sw.js")
    assert "caches.match(\"/\")" in r.text


def test_index_has_install_button():
    html = client.get("/").text
    assert "id=\"install-btn\"" in html
    assert "hidden" in html


def test_appjs_has_install_prompt_logic():
    js = client.get("/static/app.js").text
    assert "beforeinstallprompt" in js
    assert "appinstalled" in js
    assert "navigator.storage.persist" in js


def test_install_i18n_keys_in_sync():
    js = client.get("/static/app.js").text
    assert "install_btn: \"Instalar\"" in js
    assert "install_btn: \"Install\"" in js