"""Tests de comportamiento del frontend."""
import re
import subprocess
from pathlib import Path

import pytest
from app.main import app
from fastapi.testclient import TestClient


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


# ===== Módulos JS extraídos =====
# Orden de carga: los módulos deben preceder a app.js, que los consume.
STATIC = Path(__file__).resolve().parents[1] / "app" / "static"
LOAD_ORDER = ["app-i18n.js", "app-utils.js", "app.js"]


def _has_node() -> bool:
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def test_js_modules_exist():
    for name in LOAD_ORDER:
        assert (STATIC / name).is_file(), name


def test_index_loads_modules_before_app():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    positions = {}
    for name in LOAD_ORDER:
        match = re.search(rf'<script src="/static/{re.escape(name)}"></script>', html)
        assert match, name
        positions[name] = match.start()
    assert positions["app-i18n.js"] < positions["app-utils.js"] < positions["app.js"]


def test_no_duplicate_top_level_declarations():
    """Los tres scripts comparten el ámbito global: ninguna const/let puede repetirse.

    Una declaración duplicada provoca SyntaxError y deja la app entera sin
    cargar, así que este test falla rápido si alguien reintroduce el solape.
    """
    sources = [(STATIC / name).read_text(encoding="utf-8") for name in LOAD_ORDER]
    seen: dict[str, str] = {}
    for name, src in zip(LOAD_ORDER, sources, strict=True):
        for match in re.finditer(r"^(?:const|let|var) (\w+)", src, re.M):
            key = match.group(1)
            if key in seen:
                pytest.fail(
                    f"'{key}' declarado en {seen[key]} y también en {name} "
                    "(SyntaxError en el navegador)"
                )
            seen[key] = name


@pytest.mark.skipif(not _has_node(), reason="node no disponible")
def test_js_modules_parse_together():
    """node no simula <script>, pero new Function sí detecta colisiones de const."""
    sources = [
        (STATIC / name).read_text(encoding="utf-8") for name in LOAD_ORDER
    ]
    combined = ";\n".join(sources)
    script = (
        "const fs=require('fs');"
        "const s=fs.readFileSync(process.argv[1],'utf8');"
        "try{new Function(s);console.log('OK');}"
        "catch(e){console.error('ERR '+e.message);process.exit(1);}"
    )
    tmp = Path(__file__).resolve().parent / "_combined_js_check.js"
    tmp.write_text(combined, encoding="utf-8")
    result = subprocess.run(
        ["node", "-e", script, str(tmp)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_service_worker_caches_all_js_modules():
    sw = (STATIC / "sw.js").read_text(encoding="utf-8")
    for name in LOAD_ORDER:
        assert f'"/static/{name}"' in sw, name


def test_modal_focus_trap_defined_once():
    """El focus trap debe vivir en un único archivo."""
    counts = [
        (STATIC / name).read_text(encoding="utf-8").count("function trapFocus(")
        for name in LOAD_ORDER
    ]
    assert sum(counts) == 1
