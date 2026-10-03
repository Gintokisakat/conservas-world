"""Tests de microinteracciones de tarjeta y del skeleton de artículo.

Comprueban que las transiciones duren 300ms, que el botón interno de la
tarjeta reaccione al hover, y que el skeleton tenga la forma pedida
(imagen destacada + 3 líneas) con brillo y sin movimiento si se lo pide.
"""

import re

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _css() -> str:
    return client.get("/static/style.css").text


def _js() -> str:
    return client.get("/static/app.js").text


def _utils() -> str:
    return client.get("/static/app-utils.js").text


def _css_block(selector: str) -> str:
    css = _css()
    start = css.index(selector)
    return css[start : css.index("}", start)]


def _own_block(class_name: str) -> str:
    """Bloque cuya clase es exacta (evita capturar selectores compuestos)."""
    css = _css()
    start = css.index(f"\n.{class_name} {{")
    return css[start : css.index("}", start)]


def _micro() -> str:
    """Todo el bloque de microinteracciones de tarjeta."""
    css = _css()
    return css[css.index("/* ===== UX: microinteracciones de tarjeta") : css.index("/* --- Cards con elevación")]


# --- Microinteracciones --------------------------------------------------------

def test_transiciones_de_tarjeta_duran_300ms():
    block = _micro()
    transiciones = re.findall(r"(\w[\w-]*)\s+300ms", block)
    for prop in ("transform", "box-shadow", "border-color"):
        assert prop in transiciones, prop
    assert "border-color 300ms ease" in block


def test_elevacion_sutil_con_sombra_difuminada():
    block = _micro()
    hover = re.search(r"\.card-lift:hover,.*?\{(.*?)\}", block, re.S)
    assert hover, "debe existir el hover de la tarjeta"
    reglas = hover.group(1)
    assert "translateY(-4px)" in reglas
    # sombra difuminada: dos capas con spread negativo (sin borde duro)
    capas = reglas.count("px -")
    assert capas >= 2, "la sombra debe ser difusa, no una sola capa"
    assert "0 18px 38px -14px" in reglas


def test_boton_interno_cambia_de_color_al_hover():
    block = _micro()
    selector = re.search(r"(\.card-lift:hover \.card-btn,.*?)\{", block, re.S)
    assert selector, "debe haber regla para el botón interno en hover"
    cuerpo = block[selector.end() : block.index("}", selector.end())]
    assert "var(--color-accent)" in cuerpo
    assert "scale(1.14)" in cuerpo


def test_microinteracciones_aplican_a_las_tarjetas_reales():
    block = _micro()
    assert ".product-card {" in block
    assert ".product-card:hover," in block
    assert ".product-card .fav-toggle" in block
    # el HTML real genera botones .fav-toggle dentro de .product-card
    assert 'class="fav-toggle"' in client.get("/static/app.js").text


def test_sombra_ajustada_para_modo_oscuro():
    block = _micro()
    assert "html.dark .product-card:hover" in block
    oscuro = block[block.index("html.dark .card-lift:hover") :]
    assert "rgba(0, 0, 0, 0.55)" in oscuro


def test_boton_interno_conserva_foco_visible():
    block = _micro()
    assert ".product-card .fav-toggle:focus-visible" in block
    assert "outline: 2px solid var(--border-focus)" in block


def test_no_quedan_hover_duplicado_ni_transicion_corta():
    # La elevación de tarjeta vive solo en el bloque de microinteracciones:
    # el translateY(-3px) del botón del hero es otro componente.
    block = _micro()
    assert block.count("translateY(-4px)") == 1
    assert "translateY(-3px)" not in block
    assert block.count("box-shadow: var(--shadow-lg)") == 0
    # y el bloque base de la tarjeta ya no declara transición propia
    assert "transition:" not in _own_block("product-card")


def test_reduced_motion_desactiva_la_elevacion():
    css = _css()
    reduced = css[css.index("@media (prefers-reduced-motion: reduce)") :]
    assert ".product-card:hover { transform: none; }" in reduced


# --- Skeleton de artículo ------------------------------------------------------

def test_esqueleto_tiene_imagen_y_tres_lineas():
    utils = _utils()
    art = utils[utils.index("function articleSkeletons") : utils.index("function showSkeletons")]
    assert 'class="skeleton sk-media"' in art
    assert art.count('class="skeleton sk-line') == 3
    assert 'is-title' in art and 'is-text' in art and 'is-text-short' in art


def test_imagen_destacada_conserva_proporcion():
    assert "aspect-ratio: 16 / 9;" in _css_block(".skeleton-article .sk-media {")


def test_lineas_de_texto_forman_jerarquia_visual():
    assert "width: 78%;" in _css_block(".skeleton-article .sk-line.is-title {")
    assert "width: 54%;" in _css_block(".skeleton-article .sk-line.is-text-short {")
    assert "width: 100%;" in _css_block(".skeleton-article .sk-line.is-text {")


def test_brillo_animado():
    assert "@keyframes shimmer" in _css()
    assert "animation: shimmer 1.2s infinite;" in _css_block(".skeleton::after {")


def test_reduced_motion_apaga_el_brillo():
    css = _css()
    bloque = css[css.index("@media (prefers-reduced-motion: reduce) {", css.index(".skeleton-article")) :]
    assert ".skeleton::after {" in bloque
    assert "animation: none;" in bloque


def test_skeletons_escondidos_a_lectores_de_pantalla():
    utils = _utils()
    art = utils[utils.index("function articleSkeletons") : utils.index("function showSkeletons")]
    assert 'aria-hidden="true"' in art
    js = _js()
    assert 'class="sr-only"' in js
    assert 'role="status"' in js


def test_esqueleto_se_usa_en_la_carga_real_de_articulos():
    js = _js()
    bloque = js[js.index("async function loadRecipesIntoList") :][:900]
    assert "articleSkeletons(3)" in bloque
    assert 'loadingEl.classList.remove("hidden")' in bloque
    assert 'loadingEl.classList.add("hidden")' in js


def test_utilidad_hidden_oculta_de_verdad():
    """El JS alterna `.hidden`: sin esta regla el mapa nunca se ocultaba."""
    assert "display: none !important;" in _own_block("hidden")
    assert "position: absolute;" in _own_block("sr-only")


def test_contenedor_de_carga_replica_la_grilla():
    block = _css_block("#recipes-loading {")
    assert "grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));" in block