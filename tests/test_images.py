import re
from unittest.mock import patch

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
# resolve_image: orden OFF -> Commons -> Wikidata
# ---------------------------------------------------------------------------


def test_resolve_image_prioriza_off():
    p = _product_refs(["https://world.openfoodfacts.org/product/1234567890123"])
    with (
        patch.object(images, "off_image_by_barcode", return_value="https://off/front.jpg") as off,
        patch.object(images, "commons_image") as commons,
        patch.object(images, "wikidata_image") as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://off/front.jpg"
    off.assert_called_once_with("1234567890123")
    commons.assert_not_called()
    wd.assert_not_called()


def test_resolve_image_usa_mapa_off_sin_consulta():
    p = _product_refs(["https://world.openfoodfacts.org/product/1234567890123"])
    with (
        patch.object(images, "off_image_by_barcode") as off,
        patch.object(images, "commons_image") as commons,
        patch.object(images, "wikidata_image") as wd,
    ):
        url = images.resolve_image(p, off_map={"1234567890123": "https://off/map.jpg"})
    assert url == "https://off/map.jpg"
    off.assert_not_called()
    commons.assert_not_called()
    wd.assert_not_called()


def test_resolve_image_sin_off_usa_commons():
    p = _product_refs([])
    with (
        patch.object(images, "commons_image", return_value="https://commons/thumb.jpg") as commons,
        patch.object(images, "wikidata_image") as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://commons/thumb.jpg"
    commons.assert_called_once_with(p.name)
    wd.assert_not_called()


def test_resolve_image_cae_a_wikidata():
    p = _product_refs(["https://www.wikidata.org/wiki/Q12345"])
    with (
        patch.object(images, "commons_image", return_value=None) as commons,
        patch.object(images, "wikidata_image", return_value="https://commons/from-wd.jpg") as wd,
    ):
        url = images.resolve_image(p, off_map={})
    assert url == "https://commons/from-wd.jpg"
    commons.assert_called()
    wd.assert_called_once_with(p)


def test_resolve_image_retorna_none():
    p = _product_refs([])
    with (
        patch.object(images, "commons_image", return_value=None),
        patch.object(images, "wikidata_image", return_value=None),
    ):
        assert images.resolve_image(p, off_map={}) is None


def test_off_barcode_regex_acepta_variantes():
    assert re.fullmatch(images._OFF_BARCODE_RE, "openfoodfacts.org/product/12345")
    assert not re.fullmatch(images._OFF_BARCODE_RE, "openfoodfacts.org/product/abc")
