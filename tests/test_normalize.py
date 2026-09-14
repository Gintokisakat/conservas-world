from ingest.normalize import (
    _COUNTRY_ALIASES,
    extract_microbes,
    infer_categories,
    normalize_name,
    resolve_country,
)


def test_country_aliases_pre_normalized():
    """Toda clave de alias debe estar pre-normalizada (sin acentos, apóstrofes
    ni paréntesis); si no, `resolve_country` nunca la encuentra (key muerta)."""
    for key in _COUNTRY_ALIASES:
        assert normalize_name(key) == key, f"alias muerto por no estar normalizado: {key!r}"


def test_resolve_country_dr_congo_es_cd():
    """'DR Congo' y variantes deben dar República Democrática (CD), no CG."""
    for name in ("DR Congo", "DRC", "D.R. Congo", "Congo-Kinshasa", "Kinshasa"):
        info = resolve_country(name)
        assert info is not None
        assert info["iso2"] == "CD", f"{name!r} -> {info['iso2']}"


def test_resolve_country_exonimos_ingleses():
    assert resolve_country("Ivory Coast")["iso2"] == "CI"
    assert resolve_country("Burma")["iso2"] == "MM"
    assert resolve_country("Swaziland")["iso2"] == "SZ"
    assert resolve_country("Cape Verde")["iso2"] == "CV"
    assert resolve_country("Holland")["iso2"] == "NL"
    assert resolve_country("Macedonia")["iso2"] == "MK"
    assert resolve_country("East Timor")["iso2"] == "TL"


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
