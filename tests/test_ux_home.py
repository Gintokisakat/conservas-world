"""Tests de jerarquía y espaciado de la home (auditoría UX/UI).

Fijan tres correcciones:
1. El catálogo (buscador + resultados) va antes que los módulos de taller.
2. La barra de acciones separa herramientas secundarias del CTA y envuelve bien.
3. Los filtros aplicados son visibles y reversibles (chips + limpiar todo).
"""

import re

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _html() -> str:
    return client.get("/").text


def _css() -> str:
    return client.get("/static/style.css").text


def _js() -> str:
    return client.get("/static/app.js").text


def _js_i18n() -> str:
    return client.get("/static/app-i18n.js").text


def _css_block(selector: str) -> str:
    css = _css()
    start = css.index(selector)
    return css[start : css.index("}", start)]


# --- 1. Jerarquía de información ------------------------------------------------

def test_catalogo_antes_que_modulos_de_taller():
    html = _html()
    assert html.index('class="filters-card"') < html.index('class="pantry-card"')
    assert html.index('id="results"') < html.index('id="flavormap-card"')


def test_zona_de_herramientas_delimitada():
    html = _html()
    assert 'class="zone-divider"' in html
    divider = html.index('class="zone-divider"')
    assert divider < html.index('class="pantry-card"') < html.index('class="timeline-card"')


def test_tarjeta_catalogo_con_mas_peso_visual():
    block = _css_block(".filters-card {")
    assert "border-top: 3px solid var(--color-primary)" in block
    assert "var(--shadow-md)" in block


# --- 2. Barra de acciones ------------------------------------------------------

def test_acciones_agrupadas_por_prioridad():
    html = _html()
    assert 'class="form-actions-secondary"' in html
    assert 'class="form-actions-primary"' in html
    assert html.index('class="form-actions-secondary"') < html.index('class="form-actions-primary"')
    # el CTA de búsqueda sigue siendo el primer submit del formulario
    assert 'type="submit" class="btn btn-primary">Buscar' in html


def test_barra_acciones_envuelve_en_todos_los_anchos():
    block = _css_block(".form-actions {")
    assert "flex-wrap: wrap" in block
    secondary = _css_block(".form-actions-secondary {")
    assert "flex-wrap: wrap" in secondary
    assert "white-space: nowrap" in _css_block(".form-actions-secondary .btn {")
    mobile = _css_block("@media (max-width: 640px) {")
    assert "flex-wrap: normal" not in mobile


def test_cabecera_resultados_responsive():
    assert "flex-wrap: wrap" in _css_block(".results-head {")


# --- 3. Filtros aplicados visibles y reversibles --------------------------------

def test_resumen_de_filtros_en_dom():
    html = _html()
    assert 'id="active-filters"' in html
    assert 'id="clear-filters"' in html
    assert "aria-live=\"polite\"" in html


def test_js_renderiza_y_limpia_filtros():
    js = _js()
    assert "function renderActiveFilters()" in js
    assert "function activeFilterChips()" in js
    assert 'getElementById("clear-filters")?.addEventListener("click"' in js
    for key in ["category", "continent", "country", "source", "diet"]:
        assert key in js.split("const FILTER_SELECTS = ")[1].split("]")[0]


def test_chips_muestran_estado_real():
    js = _js()
    chips = js.split("function activeFilterChips()")[1].split("function renderActiveFilters()")[0]
    for token in ["gi", "semantic", "method", "onlyFavs", "q"]:
        assert f'{{ key: "{token}"' in chips


def test_sin_filtros_la_fila_se_oculta():
    js = _js()
    assert 'classList.toggle("is-empty", chips.length === 0)' in js
    assert "clearBtn.hidden = chips.length === 0" in js


def test_selects_con_aria_label_traducido():
    html = _html()
    block = _js_i18n().split("const i18n = {")[1]
    es = set(re.findall(r"^        ([a-z_]+):", block.split("    en: {")[0], re.M))
    en = set(re.findall(r"^        ([a-z_]+):", block.split("    en: {")[1].split("};")[0], re.M))
    select_keys = re.findall(r"<select id=\"([a-z]+)\"[^>]*data-i18n-aria=\"([a-z_]+)\"", html)
    assert len(select_keys) == 5
    for select_id, key in select_keys:
        assert key in es and key in en, key
        assert select_id in ["category", "continent", "country", "source", "diet"]
    assert 'querySelectorAll("[data-i18n-aria]")' in _js()