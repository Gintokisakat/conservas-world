"""Tests de la fuente FAO 1998 (Tabla 2.1)."""

from ingest.sources.fao1998 import parse_table


def _rows():
    return [
        ["Name and region", "Type of product"],
        ["Indian sub-continent", ""],
        ["Acar, Achar, Garam nimboo achar", "Pickled fruit and vegetables"],
        ["Gundruk", "Fermented dried vegetable"],
        ["Lemon pickle, Lime pickle", ""],
        ["East Asia", ""],
        ["Kimchi, Dongchimi", "Fermented in brine"],
        ["Nata de coco, Nata de pina", "Fermented fruit juice"],
        ["Africa", ""],
        ["Ogiri, Hibiscus seed", "Fermented fruit and vegetable seeds"],
        ["Wines", "Fermented fruits"],
        ["Mushrooms, Yeast", "Moulds"],
    ]


def test_parses_and_splits_names():
    records = parse_table(_rows())
    names = [r["name"] for r in records]
    assert "Acar" in names and "Garam nimboo achar" in names
    # Continuación hereda el tipo de la fila anterior.
    lemon = next(r for r in records if r["name"] == "Lemon pickle")
    assert lemon["categories"] == ["encurtido_fermentado"]


def test_category_mapping():
    records = parse_table(_rows())
    by_name = {r["name"]: r["categories"][0] for r in records}
    assert by_name["Kimchi"] == "encurtido_salmuera"
    assert by_name["Nata de coco"] == "fermento_acetico"
    assert by_name["Ogiri"] == "fermento_alcalino"


def test_skips_generics_and_headers():
    names = {r["name"] for r in parse_table(_rows())}
    assert "Wines" not in names
    assert "Mushrooms" not in names and "Yeast" not in names
    assert len(names) < sum(1 for row in _rows() for _ in row)


def test_description_mentions_region_and_fao():
    records = parse_table(_rows())
    kimchi = next(r for r in records if r["name"] == "Dongchimi")
    assert "Este Asia" in (kimchi["description"] or "")
    assert "FAO" in (kimchi["description"] or "")
    assert kimchi["references"][0]["url"].startswith("https://www.fao.org/")


def test_source_tag():
    assert all(r["source_tag"] == "fao1998" for r in parse_table(_rows()))