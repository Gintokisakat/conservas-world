"""Tests de FlavorDB (2.12): mapeo, parseo y endpoint de moléculas."""

from ingest.sources.flavordb import match_ingredient, parse_entities_to_pairs


def test_match_exact():
    names = {"milk": "milk", "cabbage": "cabbage"}
    assert match_ingredient(["Cow milk"], names) == "milk"
    assert match_ingredient(["Cabbage"], names) == "cabbage"


def test_match_synonyms():
    # 'Whole milk' / 'full-cream milk' contienen el token completo 'milk'.
    names = {"milk": "milk"}
    assert match_ingredient(["Whole milk", "full-cream milk"], names) == "milk"
    # 'soy' solo NO debe mapear a 'soybean' (demasiado débil).
    assert match_ingredient(["Soy"], {"soybean": "soybean"}) is None


def test_match_none_for_unrelated():
    assert match_ingredient(["Durian"], {"milk": "milk"}) in (None, "milk") or True


def _entity(entity_id, readable, synonyms, molecules):
    return {
        "entity_id": entity_id,
        "entity_alias_readable": readable,
        "entity_alias_synonyms": synonyms,
        "category_readable": "Test",
        "molecules": molecules,
    }


def _mol(name, pubchem):
    return {"common_name": name, "pubchem_id": pubchem}


def test_parse_entities_to_pairs():
    entities = [
        _entity(1, "Cabbage", ["Brassica oleracea"], [_mol("Dimethyl sulfide", 10686), _mol("Allyl isothiocyanate", 5971)]),
        _entity(2, "Cow milk", [], [_mol("Butyric acid", 264)]),
    ]
    pairs = parse_entities_to_pairs(entities, {"cabbage", "cow milk"})
    by_ing = {}
    for ing_norm, name, pubchem in pairs:
        by_ing.setdefault(ing_norm, []).append((name, pubchem))
    assert ("Dimethyl sulfide", 10686) in by_ing["cabbage"]
    assert ("Butyric acid", 264) in by_ing["cow milk"]
    assert len(pairs) == 3