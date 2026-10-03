"""Tests WCAG 2.1 A/AA: contraste medido, overlays por teclado, roles y foco.

El contraste no se comprueba buscando cadenas: se calculan las luminancias
WCAG y los ratios, de modo que un token nuevo que no cumpla 4.5:1 (texto) o
3:1 (bordes de control, 1.4.11) rompe la suite.
"""

import re
from pathlib import Path

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

STATIC = Path(__file__).resolve().parents[1] / "app" / "static"
CSS = (STATIC / "style.css").read_text(encoding="utf-8")
APP_JS = (STATIC / "app.js").read_text(encoding="utf-8")
UTILS_JS = (STATIC / "app-utils.js").read_text(encoding="utf-8")
I18N_JS = (STATIC / "app-i18n.js").read_text(encoding="utf-8")
JS_ALL = APP_JS + UTILS_JS + I18N_JS


# --------------------------------------------------------------------------
# Utilidades de contraste (fórmulas de WCAG 2.1, 1.4.3 y 1.4.11)
# --------------------------------------------------------------------------
def _rgb(color: str) -> tuple[float, float, float]:
    h = color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _luminance(color: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: str, bg: str) -> float:
    lf, lb = _luminance(fg), _luminance(bg)
    hi, lo = max(lf, lb), min(lf, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def tokens(scope: str = ":root") -> dict[str, str]:
    """Extrae los tokens de un bloque de tema del CSS."""
    start = CSS.index(scope)
    depth, i = 0, start
    while i < len(CSS):
        if CSS[i] == "{":
            depth += 1
        elif CSS[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    block = CSS[start:i]
    return {"--" + m.group(1): m.group(2)
            for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", block)}


LIGHT = tokens(":root")
DARK = tokens("html.dark")


# --------------------------------------------------------------------------
# 1.4.3 Contraste mínimo (texto)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("fg,bg", [
    ("--text-muted", "--bg-card"),
    ("--text-muted", "--bg-page"),
    ("--text-muted", "--color-gold-bg"),
    ("--color-accent", "--bg-card"),
    ("--color-accent", "--bg-page"),
    ("--color-gold", "--color-gold-bg"),
    ("--color-gold", "--bg-card"),
    ("--text-secondary", "--bg-card"),
    ("--text-primary", "--bg-card"),
    ("--color-primary", "--bg-card"),
])
@pytest.mark.parametrize("theme,values", [("claro", LIGHT), ("oscuro", DARK)], ids=["light", "dark"])
def test_text_contrast_4_5(theme, values, fg, bg):
    if fg not in values or bg not in values:
        pytest.skip(f"{fg}/{bg} no redefine en tema {theme}")
    ratio = contrast(values[fg], values[bg])
    assert ratio >= 4.5, f"{theme}: {fg} sobre {bg} = {ratio}:1 (minimo 4.5:1)"


@pytest.mark.parametrize("theme,values", [("claro", LIGHT), ("oscuro", DARK)], ids=["light", "dark"])
def test_non_text_contrast_3_1(theme, values):
    """1.4.11: el borde que identifica un control necesita 3:1."""
    ratio = contrast(values["--border-input"], values["--bg-card"])
    assert ratio >= 3.0, f"{theme}: --border-input sobre --bg-card = {ratio}:1 (minimo 3:1)"
    page = contrast(values["--border-input"], values["--bg-page"])
    assert page >= 3.0, f"{theme}: --border-input sobre --bg-page = {page}:1 (minimo 3:1)"
    focus = contrast(values["--border-focus"], values["--bg-card"])
    assert focus >= 3.0, f"{theme}: indicador de foco = {focus}:1 (minimo 3:1)"


def test_tag_variants_measured():
    """Las etiquetas extraidas del CSS deben cumplir 4.5:1 en ambos temas."""
    light_pairs = re.findall(r"\.tag-(?:ark|shelf|semantic|molecule|verified|safety-\w+)"
                             r"\s*\{\s*background:\s*(#[0-9a-f]{6});\s*color:\s*(#[0-9a-f]{6});", CSS)
    assert len(light_pairs) >= 6, "faltan variantes de etiqueta con color medido"
    for bg, fg in light_pairs:
        assert contrast(fg, bg) >= 4.5, f"etiqueta {fg} sobre {bg} = {contrast(fg, bg)}:1"


def test_dark_tag_variants_measured():
    pairs = re.findall(r"html\.dark \.tag-(?:ark|shelf|semantic|molecule|verified|safety-\w+)"
                       r"\s*\{\s*background:\s*(#[0-9a-f]{6});\s*color:\s*(#[0-9a-f]{6});", CSS)
    assert len(pairs) >= 6
    for bg, fg in pairs:
        assert contrast(fg, bg) >= 4.5, f"oscuro {fg} sobre {bg} = {contrast(fg, bg)}:1"


def test_no_hardcoded_low_contrast_text_colors():
    """Los rgba()/hex sueltos en plantillas JS ya no son texto de bajo contraste."""
    forbidden = ["#d96b43", "#c98836", "#b45309", "#e8b45a", "#8b5cf6", "#3b82f6", "#a9b6ad"]
    for color in forbidden:
        assert color not in JS_ALL, f"color fijo {color} fuera de los tokens (contraste no garantizado)"


def test_chart_series_are_token_based():
    assert "#c98836" not in APP_JS and "#996729" in APP_JS, "series del grafico sin token accesible"


# --------------------------------------------------------------------------
# 1.1.1 / 4.1.2 Contenido no textual y nombres accesibles
# --------------------------------------------------------------------------
def test_all_images_have_alt():
    page = client.get("/").text
    for tag in re.findall(r"<img[^>]*>", page):
        assert "alt=" in tag, tag


def test_no_unknown_css_token_used():
    assert "var(--text-color)" not in CSS and "var(--text-color)" not in JS_ALL, \
        "--text-color no existe: el color cae por herencia"


def test_aria_controls_targets_exist():
    page = client.get("/").text
    ids = set(re.findall(r'id="([^"]+)"', page))
    for control in re.findall(r'aria-controls="([^"]+)"', page):
        assert control in ids, f"aria-controls apunta a un id inexistente: {control}"


def test_view_toggles_expose_state():
    page = client.get("/").text
    assert 'id="view-list-btn"' in page and 'aria-pressed="true"' in page
    assert 'id="view-map-btn"' in page and 'aria-pressed="false"' in page
    assert 'setAttribute("aria-pressed"' in APP_JS, "setView no actualiza aria-pressed"


def test_decorative_elements_are_hidden_from_at():
    page = client.get("/").text
    assert 'class="brand-icon" aria-hidden="true"' in page
    # Un separador decorativo con aria-hidden no necesita role
    divider = page.split('class="zone-divider"')[1].split(">")[0]
    assert "role=" not in divider, "separador decorativo con role contradictorio"


def test_clickable_divs_removed():
    """2.1.1: nada de controles implementados en div/p."""
    page = client.get("/").text
    for tag in re.findall(r"<div[^>]*onclick[^>]*>", page):
        assert "modal-overlay" in tag, f"div clicable fuera de un overlay: {tag}"
    assert 'id="stats" class="stats-grid" onclick' not in page


def test_star_rating_is_a_real_slider():
    assert 'role="slider"' in APP_JS and 'tabindex="0"' in APP_JS
    assert "aria-valuenow" in APP_JS and "aria-valuetext" in APP_JS
    for key in ["ArrowRight", "ArrowLeft", "Home", "End"]:
        assert key in APP_JS, f"el deslizador de valoracion no responde a {key}"
    assert 'data-star="${v}" aria-hidden="true"' in APP_JS


# --------------------------------------------------------------------------
# 2.1.1 / 2.4.3 / 2.4.7 Overlays: Escape, trampa de Tab y devolucion del foco
# --------------------------------------------------------------------------
def test_overlay_manager_is_initialised():
    assert "function initOverlayA11y()" in UTILS_JS
    assert "initOverlayA11y();" in APP_JS, "initOverlayA11y no se invoca"


def test_focus_trap_is_actually_used():
    """trapFocus existia pero nadie la llamaba: el foco se escapaba del modal."""
    assert UTILS_JS.count("function trapFocus(") == 1
    assert "trapFocus(top, e)" in UTILS_JS, "Tab no se atrapa en el overlay abierto"
    assert "trapFocus(el)" in UTILS_JS, "abrir un overlay no mueve el foco dentro"


def test_escape_has_a_single_handler():
    """Habia dos manejadores de Escape y cerraban dos modales a la vez."""
    # 3 manejadores legitimos y distintos: autocompletado, paleta y menu movil.
    assert APP_JS.count('e.key === "Escape"') == 3, "handler de Escape duplicado o ausente"
    # El manejador del autocompletado no debe enumerar modales: esa era la lista
    # que, junto al manejador generico, cerraba dos dialogos con una sola tecla.
    suggest_handler = re.search(r'if \(e\.key === "Escape"\) closeSuggest\(\);\n\}\);', APP_JS)
    assert suggest_handler, "no se encuentra el manejador de Escape del autocompletado"
    assert "classList" not in suggest_handler.group(0)
    assert UTILS_JS.count('e.key === "Escape"') == 1


def test_overlays_cover_every_modal():
    page = client.get("/").text
    modals = set(re.findall(r'id="([a-z-]*modal[a-z-]*)"', page))
    assert len(modals) >= 17
    assert '.modal-overlay, #palette-overlay' in UTILS_JS, "el gestor debe cubrir todos los overlays"


def test_close_overlay_uses_its_own_close_button():
    assert 'overlay.querySelector(".modal-close")' in UTILS_JS, \
        "cerrar por overlay debe reutilizar la logica de cada modal"


def test_focus_returns_to_the_opening_element():
    assert "_focusBeforeOverlay" in UTILS_JS
    assert "back.focus({ preventScroll: true })" in UTILS_JS


# --------------------------------------------------------------------------
# 2.4.7 Foco visible
# --------------------------------------------------------------------------
def test_palette_input_has_focus_indicator():
    block = CSS.split("#palette-input:focus")[0].split("#palette-input {")[1]
    assert "outline: none" not in block, "el input de la paleta no puede quedarse sin foco visible"
    focus_rule = re.search(r"#palette-input:focus-visible\s*\{([^}]*)\}", CSS)
    assert focus_rule, "el input de la paleta no define anillo de foco"
    assert "outline:" in focus_rule.group(1) and "var(--border-focus)" in focus_rule.group(1)


def test_interactive_outline_none_have_visible_replacement():
    """Cada outline:none de un control debe compensarse con borde o anillo."""
    for m in re.finditer(r"([^{}]+)\{([^{}]*outline:\s*none[^{}]*)\}", CSS):
        selector, body = m.group(1).strip(), m.group(2)
        if "focus-visible" in selector or selector == ":focus":
            # el reset global :focus va seguido de :focus-visible con anillo
            continue
        has_replacement = "border-color: var(--border-focus)" in body or "box-shadow" in body
        assert has_replacement, f"{selector}: quita el outline sin indicador de foco visible"


def test_reduced_motion_is_respected():
    assert "@media (prefers-reduced-motion: reduce)" in CSS


def test_sr_only_available():
    assert ".sr-only" in CSS, "las ayudas para lectores de pantalla necesitan .sr-only"