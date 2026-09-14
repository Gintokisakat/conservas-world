import json
import re
import time
from unittest.mock import patch

import pytest

from ingest import images


def _extmeta(license_text):
    return {"LicenseShortName": {"value": license_text}}


def _page(title, thumburl, extmeta=None):
    page = {
        "title": title,
        "imageinfo": [{"thumburl": thumburl, "extmetadata": extmeta or {}}],
    }
    return page


# ---------------------------------------------------------------------------
# license_ok
# ---------------------------------------------------------------------------


def test_license_ok_acepta_cc_by():
    assert images.license_ok(_extmeta("CC BY 3.0"))


def test_license_ok_acepta_cc_by_sa():
    assert images.license_ok(_extmeta("CC BY-SA 4.0"))


def test_license_ok_acepta_cc0():
    assert images.license_ok(_extmeta("CC0 1.0"))


def test_license_ok_acepta_public_domain():
    assert images.license_ok(_extmeta("Public domain"))


def test_license_ok_rechaza_sin_metadatos():
    assert not images.license_ok(None)
    assert not images.license_ok({})


def test_license_ok_rechaza_no_commercial():
    assert not images.license_ok(_extmeta("CC BY-NC 4.0"))


def test_license_ok_rechaza_no_derivatives():
    assert not images.license_ok(_extmeta("CC BY-ND 4.0"))


def test_license_ok_rechaza_copyrighted():
    assert not images.license_ok(_extmeta("All rights reserved"))


def test_license_ok_rechaza_fair_use():
    assert not images.license_ok(_extmeta("Fair use"))


# ---------------------------------------------------------------------------
# _title_overlaps
# ---------------------------------------------------------------------------


def test_title_overlaps_coincide_token():
    assert images._title_overlaps("Kimchi", "Various kimchi with cabbage")


def test_title_overlaps_no_coincide():
    assert not images._title_overlaps("Kimchi", "Sauerkraut in a jar")


def test_title_overlaps_stopwords_no_bloquean():
    assert images._title_overlaps("Miso", "A bowl of miso soup")


# ---------------------------------------------------------------------------
# _thumb
# ---------------------------------------------------------------------------


def test_thumb_devuelve_url_sin_query_string():
    pages = [_page("Kimchi.jpg", "https://x/500px-Kimchi.jpg?utm_source=api", _extmeta("CC0"))]
    url = images._thumb(pages, "Kimchi")
    assert url == "https://x/500px-Kimchi.jpg"


def test_thumb_descarta_placeholder():
    pages = [_page("Kimchi.jpg", "https://x/file-type-icons/video.svg")]
    assert images._thumb(pages, "Kimchi") is None


def test_thumb_descarta_noise():
    pages = [_page("Map of kimchi origins.jpg", "https://x/500px-map.jpg")]
    assert images._thumb(pages, "Kimchi") is None


def test_thumb_descarta_dibujo_svg():
    pages = [_page("Kimchi logo.svg", "https://x/500px-logo.svg")]
    assert images._thumb(pages, "Kimchi") is None


def test_thumb_descarta_titulo_sin_overlap():
    pages = [_page("Red cabbage.jpg", "https://x/500px-cabbage.jpg", _extmeta("CC0"))]
    assert images._thumb(pages, "Kimchi") is None


def test_thumb_descarta_licencia_restrictiva():
    pages = [_page("Kimchi.jpg", "https://x/500px-Kimchi.jpg", _extmeta("CC BY-NC"))]
    assert images._thumb(pages, "Kimchi") is None


def test_thumb_usa_primer_candidato_valido():
    bad = _page("Kimchi 01.svg", "https://x/fileicon-svg.svg")
    good = _page("Kimchi dish.jpg", "https://x/500px-Kimchi.jpg", _extmeta("CC BY-SA 4.0"))
    assert images._thumb([bad, good], "Kimchi") == "https://x/500px-Kimchi.jpg"


# ---------------------------------------------------------------------------
# off_barcode
# ---------------------------------------------------------------------------


def _product_refs(urls):
    from app.db import models

    product = models.Product(name="X", source_tag="openfoodfacts")
    product.references = [models.Reference(title="r", url=u, ref_type="web") for u in urls]
    return product


def test_off_barcode_extrae_codigo():
    p = _product_refs(["https://world.openfoodfacts.org/product/5010292961182"])
    assert images.off_barcode(p) == "5010292961182"


def test_off_barcode_ignora_sin_refs_off():
    p = _product_refs(["https://es.wikipedia.org/wiki/Miso"])
    assert images.off_barcode(p) is None


# ---------------------------------------------------------------------------
# off_name_image: búsqueda por nombre en Open Food Facts
# ---------------------------------------------------------------------------


def test_off_name_image_devuelve_front_url():
    payload = {
        "products": [
            {"product_name": "Tempeh", "image_front_url": "https://off/front.jpg",
             "image_front_small_url": "https://off/small.jpg"},
        ]
    }
    with patch.object(images, "_fetch_off_by_name", return_value=payload):
        assert images.off_name_image("Tempeh") == "https://off/front.jpg"


def test_off_name_image_cae_a_small():
    payload = {"products": [{"product_name": "Tempeh",
                             "image_front_small_url": "https://off/small.jpg"}]}
    with patch.object(images, "_fetch_off_by_name", return_value=payload):
        assert images.off_name_image("Tempeh") == "https://off/small.jpg"


def test_off_name_image_ignora_productos_sin_foto():
    payload = {"products": [{"product_name": "Tempeh"}, {"product_name": "Kimchi"}]}
    with patch.object(images, "_fetch_off_by_name", return_value=payload):
        assert images.off_name_image("Tempeh") is None


def test_off_name_image_devuelve_primera_con_foto():
    payload = {
        "products": [
            {"product_name": "Tempeh"},
            {"product_name": "Tempeh brand", "image_front_url": "https://off/front2.jpg"},
        ]
    }
    with patch.object(images, "_fetch_off_by_name", return_value=payload):
        assert images.off_name_image("Tempeh") == "https://off/front2.jpg"


def test_resolve_image_prioriza_off_por_nombre():
    """Sin barcode OFF, la búsqueda por nombre da la foto antes que Commons."""
    p = _product_refs([])
    with (
        patch.object(images, "off_name_image", return_value="https://off/by-name.jpg") as byname,
        patch.object(images, "commons_image") as commons,
        patch.object(images, "wikidata_image") as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://off/by-name.jpg"
    byname.assert_called_once_with(p.name)
    commons.assert_not_called()
    wd.assert_not_called()


def test_resolve_image_prueba_todos_los_aliases_antes_de_wikidata():
    """Bug fix: wikidata_image no debe cortar el loop de candidates.

    Si el nombre principal no da imagen pero un alias sí (en Commons u OFF),
    se debe probar el alias ANTES de caer a Wikidata como último recurso.
    """
    from app.db import models

    p = _product_refs([])
    p.aliases = [models.ProductAlias(name="AliasConFoto", language="en")]
    with (
        patch.object(images, "off_name_image", return_value=None),
        patch.object(images, "commons_image", side_effect=[None, "https://commons/from_alias.jpg"]) as commons,
        patch.object(images, "wikidata_image", return_value=None) as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://commons/from_alias.jpg"
    assert [c.args[0] for c in commons.call_args_list] == ["X", "AliasConFoto"]
    wd.assert_not_called()


def test_resolve_image_wikidata_solo_como_ultimo_recurso():
    """Tras agotar nombre + aliases (Commons/OFF), Wikidata se usa una vez."""
    from app.db import models

    p = _product_refs([])
    p.aliases = [models.ProductAlias(name="AliasSinFoto", language="en")]
    with (
        patch.object(images, "off_name_image", return_value=None),
        patch.object(images, "commons_image", return_value=None),
        patch.object(images, "wikidata_image", return_value="https://commons/from-wd.jpg") as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://commons/from-wd.jpg"
    wd.assert_called_once_with(p)


# ---------------------------------------------------------------------------
# resolve_image: orden OFF -> Commons -> Wikidata
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_rate_limit_state():
    """Evita que el throttle global (_LAST_429) contamin entre tests."""
    images._LAST_429 = None
    yield
    images._LAST_429 = None


def test_resolve_image_prioriza_off():
    p = _product_refs(["https://world.openfoodfacts.org/product/1234567890123"])
    with (
        patch.object(images, "off_image_by_barcode", return_value="https://off/front.jpg") as off,
        patch.object(images, "off_name_image") as byname,
        patch.object(images, "commons_image") as commons,
        patch.object(images, "wikidata_image") as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://off/front.jpg"
    off.assert_called_once_with("1234567890123")
    byname.assert_not_called()
    commons.assert_not_called()
    wd.assert_not_called()


def test_resolve_image_usa_mapa_off_sin_consulta():
    p = _product_refs(["https://world.openfoodfacts.org/product/1234567890123"])
    with (
        patch.object(images, "off_image_by_barcode") as off,
        patch.object(images, "off_name_image") as byname,
        patch.object(images, "commons_image") as commons,
        patch.object(images, "wikidata_image") as wd,
    ):
        url = images.resolve_image(p, off_map={"1234567890123": "https://off/map.jpg"})
    assert url == "https://off/map.jpg"
    off.assert_not_called()
    byname.assert_not_called()
    commons.assert_not_called()
    wd.assert_not_called()


def test_resolve_image_sin_off_usa_commons():
    p = _product_refs([])
    with (
        patch.object(images, "off_name_image", return_value=None) as byname,
        patch.object(images, "commons_image", return_value="https://commons/thumb.jpg") as commons,
        patch.object(images, "wikidata_image") as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://commons/thumb.jpg"
    byname.assert_called_once_with(p.name)
    commons.assert_called_once_with(p.name)
    wd.assert_not_called()


def test_resolve_image_cae_a_wikidata():
    p = _product_refs(["https://www.wikidata.org/wiki/Q12345"])
    with (
        patch.object(images, "off_name_image", return_value=None) as byname,
        patch.object(images, "commons_image", return_value=None) as commons,
        patch.object(images, "wikidata_image", return_value="https://commons/from-wd.jpg") as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://commons/from-wd.jpg"
    byname.assert_called()
    commons.assert_called()
    wd.assert_called_once_with(p)


def test_resolve_image_retorna_none():
    p = _product_refs([])
    with (
        patch.object(images, "off_name_image", return_value=None),
        patch.object(images, "commons_image", return_value=None),
        patch.object(images, "wikidata_image", return_value=None),
    ):
        assert images.resolve_image(p, off_map={}) is None


def test_resolve_image_skip_off_no_consulta_off():
    """--skip-off debe evitar también la consulta OFF por nombre y barcode."""
    p = _product_refs(["https://world.openfoodfacts.org/product/1234567890123"])
    with (
        patch.object(images, "off_image_by_barcode") as off,
        patch.object(images, "off_name_image") as byname,
        patch.object(images, "commons_image", return_value="https://commons/thumb.jpg") as commons,
        patch.object(images, "wikidata_image") as wd,
    ):
        url = images.resolve_image(p, off_map={}, skip_off=True)
    assert url == "https://commons/thumb.jpg"
    off.assert_not_called()
    byname.assert_not_called()
    commons.assert_called_with(p.name)
    wd.assert_not_called()


def test_resolve_image_throttled_evita_fallback_wikidata(monkeypatch):
    """Con rate-limit reciente no se hace el fallback de Wikidata."""
    p = _product_refs(["https://www.wikidata.org/wiki/Q12345"])
    monkeypatch.setattr(images, "_LAST_429", 999999999.0)
    with (
        patch.object(images, "commons_image", return_value=None),
        patch.object(images, "wikidata_image") as wd,
    ):
        assert images.resolve_image(p, off_map={}) is None
    wd.assert_not_called()


def test_resolve_image_throttled_cae_a_none_sin_crash(monkeypatch):
    """Un rate-limit persistente devuelve None sin propagar RuntimeError."""
    p = _product_refs([])
    monkeypatch.setattr(images, "_LAST_429", time.monotonic())
    with (
        patch.object(images, "commons_image", side_effect=RuntimeError("agotado")),
    ):
        assert images.resolve_image(p, off_map={}) is None


def test_off_barcode_regex_acepta_variantes():
    assert re.fullmatch(images._OFF_BARCODE_RE, "openfoodfacts.org/product/12345")
    assert not re.fullmatch(images._OFF_BARCODE_RE, "openfoodfacts.org/product/abc")


# ---------------------------------------------------------------------------
# _fetch_off_by_name: caché solo en éxito (bug fix)
# ---------------------------------------------------------------------------


class _FakeResp:
    """Respuesta httpx mínima para simular la API legacy de OFF."""

    def __init__(self, status_code, body=None, json_valid=True):
        self.status_code = status_code
        self._body = body
        self._json_valid = json_valid

    def json(self):
        if self._json_valid:
            return self._body or {"products": []}
        raise ValueError("non-json")


class _FakeClient:
    def __init__(self, sequence):
        self._seq = list(sequence)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url, params=None):
        return self._seq.pop(0)


def _fast_net(monkeypatch):
    """Evita los sleeps reales de pacing/backoff en las pruebas de red."""
    monkeypatch.setattr(images, "_pace", lambda url: None)
    monkeypatch.setattr(images, "_backoff", lambda resp, attempt: 0.0)


def test_fetch_off_no_cachea_negativo_en_outage(tmp_path, monkeypatch):
    """Outage total (503): respuesta vacía y NO se escribe caché."""
    monkeypatch.setattr(images, "CACHE_DIR", tmp_path)
    _fast_net(monkeypatch)
    all_503 = [_FakeResp(503)] * 5
    with patch("httpx.Client", lambda *a, **k: _FakeClient(all_503)):
        data = images._fetch_off_by_name("kimchi")
    assert data == {"products": []}
    assert not (tmp_path / "off_name_kimchi.json").exists()


def test_fetch_off_no_cachea_negativo_en_no_json(tmp_path, monkeypatch):
    """Respuesta 200 no-JSON (rate-limit suave): tampoco se cachea negativo."""
    monkeypatch.setattr(images, "CACHE_DIR", tmp_path)
    _fast_net(monkeypatch)
    only_non_json = [_FakeResp(200, json_valid=False)] * 5
    with patch("httpx.Client", lambda *a, **k: _FakeClient(only_non_json)):
        data = images._fetch_off_by_name("kimchi")
    assert data == {"products": []}
    assert not (tmp_path / "off_name_kimchi.json").exists()


def test_fetch_off_cachea_cuando_alguno_responde(tmp_path, monkeypatch):
    """Tras un 503, la petición que responde 200+JSON sí se cachea."""
    monkeypatch.setattr(images, "CACHE_DIR", tmp_path)
    _fast_net(monkeypatch)
    mixed = [_FakeResp(503), _FakeResp(200, {"products": [{"image_front_url": "ok"}]})]
    with patch("httpx.Client", lambda *a, **k: _FakeClient(mixed)):
        data = images._fetch_off_by_name("miso")
    assert data["products"][0]["image_front_url"] == "ok"
    assert (tmp_path / "off_name_miso.json").exists()
    assert json.loads((tmp_path / "off_name_miso.json").read_text())["products"][0]["image_front_url"] == "ok"


def test_fetch_off_reusa_cache_valido(tmp_path, monkeypatch):
    """Un caché existente con datos evita la red por completo."""
    monkeypatch.setattr(images, "CACHE_DIR", tmp_path)
    _fast_net(monkeypatch)
    (tmp_path / "off_name_tempeh.json").write_text(
        json.dumps({"products": [{"image_front_url": "cached"}]}), encoding="utf-8"
    )
    with patch("httpx.Client", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no network"))):
        data = images._fetch_off_by_name("tempeh")
    assert data["products"][0]["image_front_url"] == "cached"
