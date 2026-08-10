from ingest.ingredients import (
    CANONICAL_INGREDIENTS,
    match_ingredients,
    match_ingredients_by_name,
    pick_substrate,
)


def test_match_ingredients_empty():
    assert match_ingredients("") == []
    assert match_ingredients(None) == []


def test_match_ingredients_single():
    results = match_ingredients("cabbage")
    names = [r["name"] for r in results]
    assert "cabbage" in names


def test_match_ingredients_spanish_alias():
    results = match_ingredients("repollo y sal")
    names = [r["name"] for r in results]
    assert "cabbage" in names


def test_match_ingredients_multiple():
    results = match_ingredients("cabbage, garlic, and ginger")
    names = {r["name"] for r in results}
    assert names == {"cabbage", "garlic", "ginger"}


def test_match_ingredients_max_munch():
    results = match_ingredients("coconut milk")
    names = [r["name"] for r in results]
    assert "coconut milk" in names


def test_match_ingredients_no_match():
    results = match_ingredients("quantum physics textbooks")
    assert results == []


def test_match_ingredients_deduplicates():
    results = match_ingredients("cabbage and more cabbage")
    names = [r["name"] for r in results]
    assert names.count("cabbage") == 1


def test_match_ingredients_by_name_empty():
    assert match_ingredients_by_name("") == []
    assert match_ingredients_by_name(None) == []


def test_match_ingredients_by_name_kefir():
    results = match_ingredients_by_name("Kéfir de leche")
    names = [r["name"] for r in results]
    assert "milk" in names


def test_match_ingredients_by_name_sauerkraut():
    results = match_ingredients_by_name("Sauerkraut tradicional")
    names = [r["name"] for r in results]
    assert "cabbage" in names


def test_match_ingredients_by_name_no_match():
    results = match_ingredients_by_name("random unrelated name xyz")
    assert results == []


def test_pick_substrate_prefers_vegetal():
    ingredients = [
        {"name": "cabbage", "category": "vegetal"},
        {"name": "salt", "category": "condimento"},
    ]
    assert pick_substrate(ingredients) == "cabbage"


def test_pick_substrate_prefers_cereal():
    ingredients = [
        {"name": "rice", "category": "cereal"},
        {"name": "water", "category": "otro"},
    ]
    assert pick_substrate(ingredients) == "rice"


def test_pick_substrate_none_if_empty():
    assert pick_substrate([]) is None


def test_pick_substrate_none_if_no_priority():
    ingredients = [{"name": "mystery", "category": "otro"}]
    assert pick_substrate(ingredients) is None


def test_canonical_ingredients_have_unique_names():
    names = [e["name"] for e in CANONICAL_INGREDIENTS]
    assert len(names) == len(set(names))


def test_canonical_ingredients_have_aliases():
    for entry in CANONICAL_INGREDIENTS:
        assert entry.get("aliases"), f"{entry['name']} has no aliases"
