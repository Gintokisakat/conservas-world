"""Tests de la navbar responsive y del hero.

Comprueban la estructura (logo/links/acciones), el menú hamburguesa accesible,
el CTA del hero y que ambos componentes sean responsivos.
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


def _keys(lang: str) -> set[str]:
    block = _js_i18n().split("const i18n = {")[1]
    section = block.split(f"    {lang}: {{")[1]
    return set(re.findall(r"^        ([a-z_]+):", section, re.M))


# --- Estructura de la navbar ---------------------------------------------------

def test_navbar_tres_zonas():
    html = _html()
    assert 'class="navbar"' in html
    assert 'grid-template-areas: "brand links actions"' in _css()
    assert html.index('class="brand"') < html.index('class="nav-links"')
    assert html.index('class="nav-links"') < html.index('class="nav-actions"')


def test_navbar_tiene_login_real():
    """El botón de login debe ser el auth existente, no un duplicado."""
    html = _html()
    assert html.count('id="auth-area"') == 1
    assert html.index('id="auth-area"') > html.index('class="nav-actions"')
    # renderAuthArea sustituye el contenido con el botón de entrada real
    assert 'id="login-open-btn"' in _js()


def test_enlaces_centralizados_apuntan_a_secciones_existentes():
    html = _html()
    links = re.findall(r'<li><a href="#([a-z-]+)"', html)
    assert links, "la navbar debe tener enlaces internos"
    for target in links:
        assert f'id="{target}"' in html, target


def test_solo_un_h1_en_la_pagina():
    html = _html()
    assert len(re.findall(r"<h1[\s>]", html)) == 1


# --- Hamburguesa accesible -----------------------------------------------------

def test_boton_hamburguesa_accesible():
    html = _html()
    toggle = html.split('id="nav-toggle"')[1].split(">")[0]
    assert 'aria-expanded="false"' in toggle
    assert 'aria-controls="nav-links"' in toggle
    assert 'aria-label="Abrir menú"' in toggle
    assert html.count('class="nav-toggle-bar"') == 3


def test_menu_se_abre_con_clase_y_js():
    js = _js()
    assert 'classList.toggle("is-open", open)' in js
    assert "function toggleNavMenu()" in js
    assert "function initNavMenu()" in js
    assert "menu.classList.contains(\"is-open\")" in js


def test_menu_cierra_con_escape_y_al_redimensionar():
    js = _js()
    assert 'if (e.key === "Escape"' in js
    assert "window.innerWidth > 900" in js


def test_cerrar_menu_en_escritorio():
    css = _css()
    drawer = css[css.index("@media (max-width: 900px)") : css.index("@media (max-width: 560px)")]
    assert ".nav-toggle {" in drawer
    assert "display: none" in _css_block(".nav-toggle {")
    assert ".nav-links.is-open {" in drawer
    assert "max-height: 0" in drawer


def test_label_del_boton_se_traduce():
    js = _js()
    assert 'open ? t.nav_toggle_close : t.nav_toggle_open' in js
    for lang in ("es", "en"):
        keys = _keys(lang)
        assert {"nav_toggle_open", "nav_toggle_close"} <= keys


# --- Hero ----------------------------------------------------------------------

def test_hero_primera_seccion_de_main():
    html = _html()
    main = html.index('<main class="app-container"')
    hero = html.index('class="hero"')
    catalog = html.index('id="catalog"')
    assert main < hero < catalog


def test_hero_titular_subtitulo_y_cta():
    html = _html()
    assert 'id="hero-title"' in html
    assert 'class="hero-sub"' in html
    assert 'id="hero-cta"' in html
    assert 'class="btn-hero"' in html
    assert "hero-title" in html  # el titular existe como objetivo de aria-labelledby
    assert 'aria-labelledby="hero-title"' in html


def test_hero_ocupa_la_primera_vista():
    block = _css_block(".hero {")
    assert "grid-template-columns" in block
    assert "clamp(" in _css_block(".hero-title {")
    # nada de 100vh: el catálogo debe quedar asomando bajo el hero
    assert "100vh" not in block


def test_cta_con_hover_llamativo():
    css = _css()
    btn = _css_block(".btn-hero {")
    hover = _css_block(".btn-hero:hover,")
    assert "overflow: hidden" in btn
    assert ".btn-hero::after {" in css
    assert "translateY(-3px)" in hover
    assert "translateX(120%)" in css


def test_imagen_del_hero_con_alt_y_lazy():
    html = _html()
    img = html.split('class="hero-media"')[1].split(">")[1]
    assert "/static/img/og-default.png" in img
    assert 'loading="lazy"' in img
    assert 'width="1200"' in img and 'height="630"' in img
    assert "data-i18n-alt" in img


def test_hero_responsivo():
    css = _css()
    mobile = css[css.index("@media (max-width: 560px)") :]
    assert ".hero {" in mobile
    assert "grid-template-columns: 1fr;" in mobile
    assert "aspect-ratio" in _css_block(".hero-media {")


def test_cta_enfoca_el_buscador():
    js = _js()
    block = js.split("function initHeroCta()")[1].split("function setNavMenu")[0] \
        if "function setNavMenu" in js.split("function initHeroCta()")[1] else \
        js.split("function initHeroCta()")[1]
    assert 'getElementById("q")' in block
    assert "scrollIntoView" in block
    assert "prefers-reduced-motion" in block


def test_hero_traducido():
    keys = {"hero_eyebrow", "hero_title", "hero_sub", "hero_cta",
            "hero_cta_secondary", "hero_img_alt"}
    assert keys <= _keys("es")
    assert keys <= _keys("en")
    assert 'querySelectorAll("[data-i18n-alt]")' in _js()