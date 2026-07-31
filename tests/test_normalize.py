from ingest.normalize import (
    extract_microbes,
    infer_categories,
    normalize_name,
    resolve_country,
)


def test_normalize_name_strips_accents_and_case():
    assert normalize_name("Sauerkraut") == "sauerkraut"
    assert normalize_name("Chucrut  ") == "chucrut"
    assert normalize_name("Mísó") == "miso"


def test_resolve_country_mexico():
    info = resolve_country("Mexico")
    assert info is not None
    assert info["iso2"] == "MX"
    assert info["iso3"] == "MEX"
    assert info["continent"] == "Americas"


def test_resolve_country_japan():
    info = resolve_country("Japan")
    assert info is not None
    assert info["name"] == "Japan"
    assert info["continent"] == "Asia"


def test_resolve_country_rejects_regions():
    assert resolve_country("worldwide") is None
    assert resolve_country("Southeast Asia") is None
    assert resolve_country("") is None


def test_resolve_country_finds_country_inside_region():
    info = resolve_country("Northern Benin")
    assert info is not None
    assert info["iso2"] == "BJ"
    assert info["continent"] == "Africa"


def test_resolve_country_does_not_match_partial_words():
    assert resolve_country("Armenian Highlands") is None
    assert resolve_country("Aurès Mountains") is None
    assert resolve_country("Swiss Alps") is None


def test_extract_microbes_with_species():
    assert extract_microbes("fermented by Lactobacillus acidophilus") == [
        "Lactobacillus acidophilus"
    ]


def test_extract_microbes_case_insensitive():
    assert extract_microbes("mold of aspergillus oryzae. They produce") == [
        "Aspergillus oryzae"
    ]


def test_extract_microbes_bare_genus():
    assert extract_microbes("cultured with lactobacillus") == ["Lactobacillus"]


def test_extract_microbes_ignores_stopwords():
    assert extract_microbes("lactobacillus bacteria and other species") == [
        "Lactobacillus"
    ]


def test_extract_microbes_empty():
    assert extract_microbes(None) == []
    assert extract_microbes("no microbes here") == []


def test_infer_categories_cheese():
    assert "fermento_lactico" in infer_categories("Blue cheese")


def test_infer_categories_soy_sauce():
    assert "fermento_koji" in infer_categories("Soy sauce")


def test_infer_categories_ignores_accents():
    assert "fermento_lactico" in infer_categories("Crème fraîche")


def test_infer_categories_fallback_otro():
    assert infer_categories("Something completely unrelated") == ["otro"]
