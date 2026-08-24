"""Tests de las fuentes nuevas: eAmbrosia y Wikidata profundo."""

from ingest.sources.eambrosia import parse_items
from ingest.sources.wikidata_deep import _category_for, _image_url, _val, parse_rows

# --- eAmbrosia --------------------------------------------------------------

def _gi(**overrides):
    base = {
        "giIdentifier": "EUGI00000000001",
        "protectedNames": ["Queso de Prueba", "Test Cheese"],
        "countries": ["ES"],
        "productType": "FOOD",
        "status": "registered",
        "giType": "PDO",
        "euProtectionDate": "1996-06-21",
        "cnClassification": [
            {"cnCode": "040600000080", "cnText": "0406", "cnTranslation": "04 - DAIRY | 0406 - Cheese and curd"}
        ],
        "legalInstrument": {"uri": "https://eur-lex.example/1"},
    }
    base.update(overrides)
    return base


def test_eambrosia_parses_dairy_gi():
    rows = parse_items([_gi()])
    assert len(rows) == 1
    r = rows[0]
    assert r["name"] == "Queso de Prueba"
    assert r["aliases"] == [{"name": "Test Cheese", "language": None}]
    assert r["categories"] == ["fermento_lactico"]
    assert any(c["iso2"] == "ES" and c["name"] for c in r["countries"])
    assert "DOP" in (r["description"] or "")
    assert r["source_tag"] == "eambrosia"
    assert r["references"][0]["url"].startswith("https://")


def test_eambrosia_skips_raw_agri_and_unregistered():
    rows = parse_items(
        [
            _gi(protectedNames=["Manzana Fresca"], cnClassification=[{"cnCode": "08", "cnText": "0800", "cnTranslation": "08 - Fruit"}]),
            _gi(status="pending"),
            _gi(productType="WINE"),
            _gi(giIdentifier=None),
        ]
    )
    assert rows == []


def test_eambrosia_maps_cured_meat_and_pickles():
    rows = parse_items(
        [
            _gi(protectedNames=["Salchichón X"], cnClassification=[{"cnCode": "1601", "cnText": "1601", "cnTranslation": "16 - Sausages"}]),
            _gi(protectedNames=["Pepinillo Y"], cnClassification=[{"cnCode": "2001", "cnText": "2001", "cnTranslation": "20 - Vegetables prepared with vinegar"}]),
            _gi(protectedNames=["Mermelada Z"], cnClassification=[{"cnCode": "2007", "cnText": "2007", "cnTranslation": "20 - Jams"}]),
        ]
    )
    cats = {r["name"]: r["categories"] for r in rows}
    assert cats["Salchichón X"] == ["curado_sal"]
    assert cats["Pepinillo Y"] == ["encurtido_vinagre"]
    assert cats["Mermelada Z"] == ["conserva_azucar"]


def test_eambrosia_dedupes_same_name():
    rows = parse_items([_gi(), _gi(giIdentifier="EUGI00000000002")])
    assert len(rows) == 1


# --- Wikidata deep ----------------------------------------------------------

def _binding(item="http://www.wikidata.org/entity/Q999999", **kw):
    def lit(v):
        return {"value": v} if v is not None else None

    row = {
        "item": lit(item),
        "rootQid": lit(kw.pop("root", "Q10943")),
        "labelEn": lit(kw.pop("labelEn", None)),
        "labelEs": lit(kw.pop("labelEs", None)),
        "iso2": lit(kw.pop("iso2", None)),
        "imageFile": lit(kw.pop("imageFile", None)),
        "clsLabel": lit(kw.pop("clsLabel", None)),
    }
    row = {k: v for k, v in row.items() if v is not None}
    return row


def test_wikidata_val_helper():
    assert _val({"value": "x"}) == "x"
    assert _val("raw") == "raw"
    assert _val(None) is None


def test_wikidata_parse_row_aggregation():
    rows = [
        _binding(labelEs="Kimchi de prueba", labelEn="Test kimchi", iso2="KR", imageFile="Kimchi 3.jpg"),
        # Segunda fila del mismo ítem con otro país (multi-país).
        _binding(iso2="CN"),
    ]
    records = parse_rows(rows)
    assert len(records) == 1
    r = records[0]
    assert r["name"] == "Kimchi de prueba"
    assert {"name": "Test kimchi", "language": "en"} in r["aliases"]
    assert {c["iso2"] for c in r["countries"]} == {"KR", "CN"}
    assert r["image_url"] and "Special:FilePath" in r["image_url"]
    assert r["_qid"] == "Q999999"


def test_wikidata_category_mapping():
    assert _category_for("Q10943", set()) == "fermento_lactico"
    assert _category_for("Q3506176", set()) == "fermento_lactico"
    assert _category_for(None, {"soybean dish"}) == "fermento_koji"
    assert _category_for(None, {"rice wine"}) == "fermento_alcoholico"
    assert _category_for(None, {"pickled cabbage dish"}) == "encurtido_fermentado"
    assert _category_for("Q6950796", {"unknown thing"}) == "otro"


def test_wikidata_skips_junk():
    assert parse_rows([]) == []
    rows = [_binding(item="not-a-uri")]
    assert parse_rows(rows) == []


def test_image_url_encoding():
    url = _image_url("Kimchi con ñ.jpg")
    assert url is not None and "%C3%B1" in url


def test_wikidata_skips_wine_appellations():
    rows = [
        # Apelación italiana con descripción típica -> se descarta.
        _binding(labelEs="Bardolino Chiaretto spumante DOC",
                 labelEn="Bardolino Chiaretto",
                 clsLabel="wine",
                 imageFile=None),
        # Queso legítimo -> se conserva.
        _binding(labelEs="Comté", labelEn="Comté cheese", clsLabel="cheese"),
    ]
    records = parse_rows(rows)
    assert [r["name"] for r in records] == ["Comté"]
    assert records[0]["categories"] == ["fermento_lactico"]