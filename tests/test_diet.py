
from app.services.diet import (
    DIET_TAGS,
    REQUIRED,
    VIOLATIONS,
    ingredient_diet_tags,
    product_diet_tags,
)


class _Ing:
    def __init__(self, name, category):
        self.name = name
        self.category = category


def test_vegan_simple():
    tags = product_diet_tags([_Ing("cabbage", "vegetal"), _Ing("salt", "otro")])
    assert "vegan" in tags
    assert "vegetarian" in tags
    assert "spicy" not in tags


def test_meat_blocks_vegan_and_vegetarian():
    tags = product_diet_tags([_Ing("pork", "carne")])
    assert "vegan" not in tags
    assert "vegetarian" not in tags
    assert "pescatarian" not in tags


def test_fish_blocks_vegan_vegetarian_but_allows_pescatarian():
    tags = product_diet_tags([_Ing("anchovy", "pescado")])
    assert "vegan" not in tags
    assert "vegetarian" not in tags
    assert "pescatarian" in tags


def test_dairy_blocks_vegan_but_allows_vegetarian():
    tags = product_diet_tags([_Ing("milk", "lacteo")])
    assert "vegan" not in tags
    assert "vegetarian" in tags
    assert "dairy_free" not in tags


def test_gluten_blocks_gluten_free():
    tags = product_diet_tags([_Ing("wheat", "cereal")])
    assert "gluten_free" not in tags


def test_rice_is_gluten_free():
    tags = product_diet_tags([_Ing("rice", "cereal")])
    assert "gluten_free" in tags


def test_soy_blocks_soy_free():
    tags = product_diet_tags([_Ing("soybean", "legumbre")])
    assert "soy_free" not in tags


def test_nut_blocks_nut_free():
    tags = product_diet_tags([_Ing("peanut", "legumbre")])
    assert "nut_free" not in tags


def test_spicy_positive():
    tags = product_diet_tags([_Ing("chili", "vegetal")])
    assert "spicy" in tags
    assert "vegan" in tags


def test_egg_blocks_egg_free():
    tags = product_diet_tags([_Ing("egg", "otro")])
    assert "egg_free" not in tags
    assert "vegan" not in tags


def test_no_ingredients_returns_empty():
    assert product_diet_tags([]) == []


def test_combined_miso():
    tags = product_diet_tags([_Ing("soybean", "legumbre"), _Ing("rice", "cereal")])
    assert "vegan" in tags
    assert "soy_free" not in tags
    assert "gluten_free" in tags


def test_diet_tags_ordering_is_stable():
    tags = product_diet_tags([_Ing("cabbage", "vegetal")])
    assert tags == sorted(tags, key=DIET_TAGS.index)


def test_ingredient_diet_tags_api():
    tags = ingredient_diet_tags("chili", "vegetal")
    assert "spicy" in tags


def test_violations_and_required_sets_consistent():
    for tag in DIET_TAGS:
        assert isinstance(VIOLATIONS[tag], set)
        assert isinstance(REQUIRED[tag], set)
    assert REQUIRED["spicy"] == {"chili", "black pepper", "gochujang"}
