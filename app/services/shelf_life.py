"""Shelf-life con FSIS FoodKeeper (2.15).

Guías de vida útil por categoría de alimento fermentado, curadas en código
según el espíritu de los datos de FSIS FoodKeeper (USDA). Sin descargas
externas ni escrituras en la base de datos.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ShelfLife:
    category: str
    keywords: tuple[str, ...]
    fridge_days: int
    freezer_days: int | None
    pantry_days: int | None
    notes_es: str
    notes_en: str


PROFILES: tuple[ShelfLife, ...] = (
    ShelfLife(
        "Vegetales lactofermentados",
        ("chucrut", "sauerkraut", "kimchi", "curtido", "encurtido", "pickle", "pepinillo", "repollo", "cabbage", "col"),
        90, 360, None,
        "Conservado por acidez (pH < 4,6). En la nevera mantiene sabor y probióticos; congela si pierde textura.",
        "Preserved by acidity (pH < 4.6). In the fridge it keeps flavour and probiotics; freeze if texture declines.",
    ),
    ShelfLife(
        "Salmuera de vegetales",
        ("salmuera", "brine", "aceituna", "olive", "alcaparra", "capers"),
        180, 540, 60,
        "En salmuera abierta dura meses en frío. A temperatura ambiente, solo conservas sin abrir.",
        "Open brine lasts months refrigerated. At room temperature, only unopened preserves.",
    ),
    ShelfLife(
        "Fermentos de soja",
        ("miso", "shoyu", "soja", "tamari", "tempeh"),
        720, None, None,
        "El miso y el shoyu mejoran con el tiempo en frío; el tempeh solo dura unos días en la nevera.",
        "Miso and shoyu improve over time when cold; tempeh only lasts a few days refrigerated.",
    ),
    ShelfLife(
        "Té fermentado",
        ("kombucha", "booch"),
        45, 180, 7,
        "Segunda fermentación en frío frena la acidez. Se conserva semanas en la nevera; congélalo como hielo de arranque.",
        "Cold second ferment slows acidity. Lasts weeks refrigerated; freeze as starter ice cubes.",
    ),
    ShelfLife(
        "Lácteos fermentados",
        ("yogur", "yogurt", "kéfir", "kefir", "skyr", "cuajada"),
        21, 180, None,
        "Refrigerados duran ~3 semanas si están bien cerrados. El kéfir continúa fermentando lentamente en frío.",
        "Refrigerated, they last ~3 weeks if well sealed. Kefir keeps fermenting slowly when cold.",
    ),
    ShelfLife(
        "Quesos",
        ("queso", "cheese", "cheddar", "mozzarella", "brie", "camembert", "parmesano", "feta"),
        90, 240, None,
        "Quesos duros duran meses; los frescos y de corteza florida, 1-3 semanas. No congelar quesos frescos.",
        "Hard cheeses last months; fresh and bloomy-rind ones, 1-3 weeks. Do not freeze fresh cheeses.",
    ),
    ShelfLife(
        "Salsas de pescado",
        ("garum", "salsa de pescado", "fish sauce", "nam pla", "nuoc mam"),
        1800, None, 540,
        "Muy saladas y ácidas: duran años a temperatura ambiente; en frío se prolonga aún más.",
        "Very salty and acidic: they last years at room temperature; cold storage extends them further.",
    ),
    ShelfLife(
        "Vinagres",
        ("vinagre", "vinegar", "sikbaj", "acético"),
        3600, None, 3600,
        "El ácido acético lo hace casi imperecedero; la 'madre' indica fermento activo, no deterioro.",
        "Acetic acid makes it nearly permanent; the 'mother' signals active fermentation, not spoilage.",
    ),
    ShelfLife(
        "Carnes curadas",
        ("salchichón", "chorizo", "jamón", "salami", "prosciutto"),
        90, 180, None,
        "Curados secos duran semanas-meses refrigerados; cortar moho superficial y no conservar si hay olor anómalo.",
        "Dry-cured meats last weeks to months refrigerated; trim surface mould and discard on odd odour.",
    ),
    ShelfLife(
        "Granos fermentados",
        ("masa madre", "sourdough", "levadura", "pan", "koji", "malt"),
        14, 360, 7,
        "El pan de masa madre dura ~1 semana; el koji y los cultivos de grano se congelan para prolongar su vida.",
        "Sourdough bread lasts ~1 week; koji and grain cultures freeze to extend their life.",
    ),
)


def lookup(term: str) -> ShelfLife | None:
    t = term.lower().strip()
    if not t:
        return None
    for p in PROFILES:
        for k in p.keywords:
            if re.search(rf"\b{re.escape(k)}\b", t):
                return p
    return None


def shelf_life_out(p: ShelfLife, lang: str = "es") -> dict:
    is_en = lang == "en"
    return {
        "category": p.category,
        "fridge_days": p.fridge_days,
        "freezer_days": p.freezer_days,
        "pantry_days": p.pantry_days,
        "notes": p.notes_en if is_en else p.notes_es,
    }