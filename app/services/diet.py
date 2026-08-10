"""Etiquetas dietarias derivadas de los ingredientes canonicos.

Las reglas se evaluan a partir de nombre + categoria de cada ingrediente.
Las etiquetas de exclusion (vegan, gluten_free, etc.) se asignan a un
producto solo si tiene ingredientes y ninguno de ellos viola la regla.
Las etiquetas positivas (spicy) se asignan si al menos un ingrediente la
cumple.
"""

from ingest.ingredients import CANONICAL_INGREDIENTS

ANIMAL_CATEGORIES = {"carne", "pescado", "marisco", "lacteo"}
MEAT_CATEGORIES = {"carne", "pescado", "marisco"}
RED_MEAT_CATEGORIES = {"carne"}

GLUTEN_NAMES = {"wheat", "barley", "rye", "malt", "bread", "flour", "sourdough"}
SOY_NAMES = {"soybean", "soy sauce", "miso", "tofu", "tempeh", "natto", "okara", "douchi"}
NUT_NAMES = {"peanut", "walnut", "cashew"}
SPICY_NAMES = {"chili", "black pepper", "gochujang"}
NON_VEGAN_SPECIFIC = {"egg", "gelatin", "honey"}

# Orden de presentacion en la UI.
DIET_TAGS = [
    "vegan",
    "vegetarian",
    "pescatarian",
    "gluten_free",
    "dairy_free",
    "soy_free",
    "nut_free",
    "egg_free",
    "spicy",
]


def ingredient_diet_tags(name: str, category: str | None) -> set[str]:
    """Etiquetas aplicables a un ingrediente individual."""
    tags: set[str] = set()
    if name in SPICY_NAMES:
        tags.add("spicy")
    if category not in ANIMAL_CATEGORIES and name not in NON_VEGAN_SPECIFIC:
        tags.add("vegan")
    if category not in MEAT_CATEGORIES:
        tags.add("vegetarian")
    if category not in RED_MEAT_CATEGORIES:
        tags.add("pescatarian")
    if name not in GLUTEN_NAMES:
        tags.add("gluten_free")
    if category != "lacteo":
        tags.add("dairy_free")
    if name not in SOY_NAMES:
        tags.add("soy_free")
    if name not in NUT_NAMES:
        tags.add("nut_free")
    if name != "egg":
        tags.add("egg_free")
    return tags


def product_diet_tags(ingredients) -> list[str]:
    """Etiquetas de un producto dado el iterable de ingredientes (objetos
    con atributos ``name`` y ``category`` o dicts con esas claves)."""
    names_cats = []
    for ing in ingredients:
        if isinstance(ing, dict):
            name = ing.get("name")
            category = ing.get("category")
        else:
            name = getattr(ing, "name", None)
            category = getattr(ing, "category", None)
        if name:
            names_cats.append((name, category))

    if not names_cats:
        return []

    tags = set()
    positive = set()
    for name, category in names_cats:
        ing_tags = ingredient_diet_tags(name, category)
        positive |= ing_tags & {"spicy"}
        if name in GLUTEN_NAMES:
            tags.add("gluten_free_blocked")
        if category == "lacteo":
            tags.add("dairy_free_blocked")
        if name in SOY_NAMES:
            tags.add("soy_free_blocked")
        if name in NUT_NAMES:
            tags.add("nut_free_blocked")
        if name == "egg":
            tags.add("egg_free_blocked")
        if category in ANIMAL_CATEGORIES or name in NON_VEGAN_SPECIFIC:
            tags.add("vegan_blocked")
        if category in MEAT_CATEGORIES:
            tags.add("vegetarian_blocked")
        if category in RED_MEAT_CATEGORIES:
            tags.add("pescatarian_blocked")

    result = set(positive)
    for tag in ["vegan", "vegetarian", "pescatarian", "gluten_free", "dairy_free", "soy_free", "nut_free", "egg_free"]:
        if f"{tag}_blocked" not in tags:
            result.add(tag)

    return [t for t in DIET_TAGS if t in result]


def _violating_names(tag: str) -> set[str]:
    """Nombres canonicos que bloquean la etiqueta de exclusion dada."""
    if tag not in DIET_TAGS or tag == "spicy":
        return set()
    return {
        entry["name"]
        for entry in CANONICAL_INGREDIENTS
        if tag not in ingredient_diet_tags(entry["name"], entry["category"])
    }


def _required_names(tag: str) -> set[str]:
    """Nombres canonicos requeridos para la etiqueta positiva dada."""
    if tag == "spicy":
        return SPICY_NAMES
    return set()


VIOLATIONS: dict[str, set[str]] = {tag: _violating_names(tag) for tag in DIET_TAGS}
REQUIRED: dict[str, set[str]] = {tag: _required_names(tag) for tag in DIET_TAGS}
