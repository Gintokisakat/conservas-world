"""Tests de accesibilidad (4.10): skip-link, landmarks ARIA, aria-live y etiquetas."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _page() -> str:
    return client.get("/").text


def test_skip_link_present():
    page = _page()
    assert 'class="skip-link"' in page
    assert '#main-content' in page


def test_main_landmark():
    assert 'id="main-content"' in _page()


def test_modals_are_dialogs():
    page = _page()
    for modal_id in ["detail", "ingredient-modal", "shopping-modal", "microbes-modal",
                     "trouble-modal", "label-modal", "charts-modal", "guide-modal",
                     "glossary-modal"]:
        assert f'id="{modal_id}"' in page
        block = page.split(f'id="{modal_id}"')[1].split(">")[0]
        assert "role=\"dialog\"" in block, modal_id
        assert "aria-modal=\"true\"" in block, modal_id
        assert "aria-label" in block, modal_id


def test_all_modal_close_buttons_have_aria_label():
    page = _page()
    import re

    close_buttons = re.findall(r'class="modal-close"[^>]*>', page)
    assert len(close_buttons) >= 9
    for btn in close_buttons:
        assert "aria-label" in btn, btn


def test_live_regions():
    page = _page()
    assert 'id="count" class="count-badge" aria-live="polite"' in page
    assert 'id="timers-list" class="timers-grid" aria-live="polite"' in page
    assert 'id="recommendations"' in page and "aria-live=\"polite\"" in page
    assert 'id="map-loading"' in page and "aria-live=\"polite\"" in page


def test_search_combobox_attributes():
    page = _page()
    assert 'role="combobox"' in page
    assert "aria-expanded" in page
    assert "aria-autocomplete=\"list\"" in page


def test_css_has_focus_visible_and_reduced_motion():
    css = client.get("/static/style.css").text
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css
    assert ".skip-link" in css


def test_theme_toggle_has_aria_label():
    assert 'aria-label="Cambiar tema"' in _page()


def test_escape_closes_ingredient_modal():
    js = client.get("/static/app.js").text
    assert 'ingredient-modal").classList.add("hidden"' in js