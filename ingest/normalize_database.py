"""Normaliza la base de datos: nombres multilingües a español, títulos rotos,
barcodes/números y descripciones con ruido. Guarda el nombre original como alias.

Uso:
    python -m ingest.normalize_database [--dry-run] [--limit N]
"""

import argparse
import re
from collections import Counter

from app.db import models
from app.db.database import SessionLocal

# ---------------------------------------------------------------------------
# Lexicón: frases y palabras por idioma -> español. Las frases se intentan
# primero (más largas primero); las palabras sueltas después.
# ---------------------------------------------------------------------------

_PHRASES: dict[str, list[tuple[str, str]]] = {
    "en": [
        ("pickled gherkins", "pepinillos encurtidos"),
        ("sweet pickled", "agridulces"),
        ("pickled onions", "cebollas encurtidas"),
        ("pickled cucumbers", "pepinos encurtidos"),
        ("pickled vegetables", "verduras encurtidas"),
        ("sweet and sour", "agridulce"),
        ("sweet-and-sour", "agridulce"),
        ("in brine", "en salmuera"),
        ("in vinegar", "en vinagre"),
        ("in oil", "en aceite"),
        ("in salt", "en sal"),
        ("apple cider", "sidra de manzana"),
        ("cider vinegar", "vinagre de sidra"),
        ("apple cider vinegar", "vinagre de sidra de manzana"),
        ("red wine vinegar", "vinagre de vino tinto"),
        ("white wine vinegar", "vinagre de vino blanco"),
        ("balsamic vinegar", "vinagre balsámico"),
        ("wine vinegar", "vinagre de vino"),
        ("sea salt", "sal marina"),
        ("olive oil", "aceite de oliva"),
        ("extra virgin", "virgen extra"),
        ("soy sauce", "salsa de soja"),
        ("fish sauce", "salsa de pescado"),
        ("hot sauce", "salsa picante"),
        ("chilli sauce", "salsa de chile"),
        ("chili sauce", "salsa de chile"),
        ("bean curd", "tofu"),
        ("bean paste", "pasta de soja"),
        ("fermented bean paste", "pasta de soja fermentada"),
        ("fermented bean curd", "tofu fermentado"),
        ("fermented milk products", "productos lácteos fermentados"),
        ("milk products", "productos lácteos"),
        ("cod liver oil", "aceite de hígado de bacalao"),
        ("shrimp paste", "pasta de gambas"),
        ("soybean paste", "pasta de soja"),
        ("soy bean paste", "pasta de soja"),
        ("cucumber soup", "sopa de pepino"),
        ("soured milk", "leche agria"),
        ("chilli and", "chile y"),
        ("sweet soy", "soja dulce"),
        ("smoked salmon", "salmón ahumado"),
        ("sourdough bread", "pan de masa madre"),
        ("coconut milk", "leche de coco"),
        ("dark chocolate", "chocolate negro"),
        ("milk chocolate", "chocolate con leche"),
        ("free range", "de corral"),
        ("gluten free", "sin gluten"),
        ("no added", "sin añadir"),
    ],
    "fr": [
        ("cornichons aigres-doux", "pepinillos agridulces"),
        ("aigres-doux", "agridulce"),
        ("extra-fins", "extra finos"),
        ("extra fins", "extra finos"),
        ("au vinaigre", "en vinagre"),
        ("vinaigre de vin", "vinagre de vino"),
        ("vinaigre balsamique", "vinagre balsámico"),
        ("huile d'olive", "aceite de oliva"),
        ("huile de colza", "aceite de colza"),
        ("en saumure", "en salmuera"),
        ("sans sucre", "sin azúcar"),
        ("sans sucre ajouté", "sin azúcar añadido"),
        ("au sel", "con sal"),
        ("de mer", "de mar"),
        ("fumé", "ahumado"),
        ("fumée", "ahumada"),
        ("petit", "pequeño"),
        ("à l'ancienne", "a la antigua"),
        ("aux épices", "con especias"),
        ("et aromates", "y aromáticas"),
        ("de la mer", "de mar"),
        ("au naturel", "al natural"),
        ("biologique", "ecológico"),
    ],
    "de": [
        ("eingelegte gurken", "pepinillos encurtidos"),
        ("gurken in", "pepinillos en"),
        ("knoblauch eingelegt", "ajo encurtido"),
        ("sauerkraut", "chucrut"),
        ("rotkohl", "lombarda"),
        ("rote beete", "remolacha"),
        ("in scheiben", "en rodajas"),
        ("in öl", "en aceite"),
        ("in essig", "en vinagre"),
        ("ohne zucker", "sin azúcar"),
        ("mit chilli", "con chile"),
        ("mit knoblauch", "con ajo"),
        ("mit dill", "con eneldo"),
        ("mit senf", "con mostaza"),
        ("biologisch", "ecológico"),
        ("naturbelassen", "natural"),
        ("aus der region", "de la región"),
        ("zum sofortigen verzehr", "para consumo inmediato"),
    ],
    "it": [
        ("sottaceti", "encurtidos"),
        ("sott'olio", "en aceite"),
        ("in agrodolce", "agridulce"),
        ("aceto balsamico", "vinagre balsámico"),
        ("olio di oliva", "aceite de oliva"),
        ("al naturale", "al natural"),
        ("naturale biologico", "natural ecológico"),
        ("formaggio stagionato", "queso curado"),
        ("pasta di acciughe", "pasta de anchoas"),
    ],
    "pt": [
        ("pimenta moida", "pimiento molido"),
        ("pepino em", "pepino en"),
        ("em conserva", "en conserva"),
        ("azeite de oliva", "aceite de oliva"),
        ("vinagre de vinho", "vinagre de vino"),
        ("queijo fresco", "queso fresco"),
        ("iogurte natural", "yogur natural"),
        ("agridoce", "agridulce"),
        ("tradicional", "tradicional"),
    ],
    "pl": [
        ("kapusta kiszona", "repollo fermentado"),
        ("ogórki kiszone", "pepinillos fermentados"),
        ("ogórki konserwowe", "pepinillos encurtidos"),
        ("czosnek w oleju", "ajo en aceite"),
        ("w sosie", "en salsa"),
        ("naturalny", "natural"),
    ],
    "nl": [
        ("zoetzuur", "agridulce"),
        ("augurken zoetzuur", "pepinillos agridulces"),
        ("augurken plakjes", "rodajas de pepinillos"),
        ("in het zuur", "encurtido"),
        ("natuurlijk", "natural"),
    ],
}

_WORDS: dict[str, dict[str, str]] = {
    "en": {
        "the": "", "a": "", "an": "", "of": "de", "with": "con", "and": "y", 
        "for": "para", "on": "sobre", "by": "por", "from": "de", "to": "a", "at": "en",
        "apples": "manzanas", "vinegar": "vinagre",
        "balsamic": "balsámico", "red": "rojo", "white": "blanco", "wine": "vino",
        "raw": "crudo", "sauerkraut": "chucrut", "cabbage": "repollo",
        "kimchi": "kimchi", "pickled": "encurtido", "pickle": "pepinillo", "pickles": "pepinillos",
        "gherkins": "pepinillos", "gherkin": "pepinillo", "cucumber": "pepino", "cucumbers": "pepinos",
        
        "dried": "seco", "fermented": "fermentado", "cheese": "queso",
        "milk": "leche", "yogurt": "yogur", "yoghurt": "yogur", "kefir": "kéfir",
        "butter": "mantequilla", "cream": "crema", "beer": "cerveza", "ale": "cerveza",
        "sake": "sake", "kombucha": "kombucha", "miso": "miso",
        "tempeh": "tempeh", "natto": "natto", "tofu": "tofu",         "soy": "soja", "soya": "soja",
        "list": "lista", "foods": "alimentos", "food": "alimento", "products": "productos",
        "sauce": "salsa", "soybean": "soja", "bean": "frijol", "beans": "frijoles",
        "oil": "aceite", "olive": "aceituna", "olives": "aceitunas", "sea": "mar", "salt": "sal",
        "sardines": "sardinas", "sardine": "sardina", "anchovies": "anchoas", "anchovy": "anchoa",
        "tuna": "atún", "mackerel": "caballa", "herring": "arenque", "salmon": "salmón",
        "fish": "pescado", "shrimp": "gambas", "prawn": "gamba", "crab": "cangrejo",
        "mussels": "mejillones", "oysters": "ostras", "squid": "calamar", "octopus": "pulpo",
        "caviar": "caviar", "jam": "mermelada", "marmalade": "mermelada", "honey": "miel",
        "fruit": "fruta", "fruits": "frutas", "lemon": "limón", "orange": "naranja",
        "mango": "mango", "strawberry": "fresa", "strawberries": "fresas", "raspberry": "frambuesa",
        "blackberry": "mora", "blueberry": "arándano", "cherry": "cereza", "cherries": "cerezas",
        "apple": "manzana", "pear": "pera", "peach": "melocotón", "apricot": "albaricoque",
        "plum": "ciruela", "pineapple": "piña", "coconut": "coco", "banana": "plátano",
        "grape": "uva", "grapes": "uvas", "fig": "higo", "dates": "dátiles", "date": "dátil",
        "garlic": "ajo", "onion": "cebolla", "onions": "cebollas", "shallots": "chalotas",
        "ginger": "jengibre", "chilli": "chile", "chili": "chile", "pepper": "pimiento",
        "peppers": "pimientos", "mustard": "mostaza", "seeds": "semillas", "seed": "semilla",
        "capers": "alcaparras", "caper": "alcaparra", "artichoke": "alcachofa",
        "beetroot": "remolacha", "beet": "remolacha", "carrot": "zanahoria", "carrots": "zanahorias",
        "radish": "rábano", "daikon": "daikon", "turnip": "nabo", "celery": "apio",
        "eggplant": "berenjena", "courgette": "calabacín", "zucchini": "calabacín",
        "pumpkin": "calabaza", "tomato": "tomate", "tomatoes": "tomates", "corn": "maíz",
        "maize": "maíz", "rice": "arroz", "barley": "cebada", "oats": "avena",
        "rye": "centeno", "mushroom": "champiñón", "mushrooms": "champiñones", "bamboo": "bambú",
        "aubergine": "berenjena", "herbs": "hierbas", "herb": "hierba", "basil": "albahaca",
        "dill": "eneldo", "parsley": "perejil", "chives": "cebolino", "rosemary": "romero",
        "thyme": "tomillo", "oregano": "orégano", "paprika": "pimentón", "curry": "curry",
        "turmeric": "cúrcuma", "cinnamon": "canela", "cloves": "clavo", "nutmeg": "nuez moscada",
        "green": "verde", "yellow": "amarillo", "brown": "marrón",
        "sweet": "dulce", "sour": "agrio", "spicy": "picante", "hot": "picante", "mild": "suave",
        "aged": "curado", "cured": "curado", "fresh": "fresco",
        "natural": "natural", "classic": "clásico", "traditional": "tradicional",
        "artisan": "artesano", "artisanal": "artesano", "homemade": "casero", "premium": "premium",
        "finest": "selección", "organic": "ecológico", "free": "sin", "style": "estilo",
        "flavoured": "saborizado", "flavored": "saborizado", "roasted": "tostado",
        "grilled": "a la parrilla", "fried": "frito", "cooked": "cocido", "boiled": "hervido",
        "sliced": "en rodajas", "cut": "troceado", "whole": "enteros", "pieces": "trozos",
        "chunks": "trozos", "stuffed": "rellenos", "pitted": "deshuesadas", "seedless": "sin semillas",
        "in": "en", "brine": "salmuera", "water": "agua", "sugar": "azúcar", "syrup": "almíbar",
        "dark": "negro", "large": "grande", "small": "pequeño",
        "first": "primera", "quality": "calidad", "extra": "extra",
        "deli": "gourmet", "dry": "seco", "smoked": "ahumado",
        "salted": "salado", "house": "casa", "soup": "sopa", "paste": "pasta",
        "powder": "polvo", "tea": "té", "coffee": "café", "juice": "zumo", "lemonade": "limonada",
        "soda": "gaseosa", "still": "sin gas", "mineral": "mineral",
        "cane": "caña", "molasses": "melaza", "barrel": "barrica", 
        "oak": "roble", "malt": "malta", "hops": "lúpulo", "lager": "lager", "pilsner": "pilsner",
        "stout": "stout", "porter": "porter", "wheat": "trigo", "whisky": "whisky",
        "brandy": "brandy", "rum": "ron", "gin": "ginebra", "vodka": "vodka", "tequila": "tequila",
        "mead": "hidromiel", "spirit": "licor", "cider": "sidra", "liqueur": "licor",
        "mountain": "de montaña", "valley": "del valle", "island": "de isla",
        "chinese": "chino", "japanese": "japonés", "korean": "coreano", "italian": "italiano",
        "french": "francés", "german": "alemán", "greek": "griego", "spanish": "español",
        "turkish": "turco", "indian": "indio", "thai": "tailandés", "vietnamese": "vietnamita",
        "moroccan": "marroquí", "mexican": "mexicano", "swiss": "suizo", "dutch": "neerlandés",
        "belgian": "belga", "portuguese": "portugués", "lychee": "lichi", "pine": "pino",
        "glazed": "glasé", "crystallized": "cristalizado", "preserved": "en conserva",
        "preserve": "conserva", "preserves": "conservas", "black": "negro", "golden": "dorado",
        "pale": "pálido", "amber": "ámbar", "light": "suave",
        "rose": "rosado", "semi": "semiseco", "sparkling": "espumoso", 
    },
    "fr": {
        "le": "", "la": "", "les": "", "un": "", "une": "", "des": "de", "du": "de",
        "de": "de", "d'": "de", "l'": "", "au": "con", "aux": "con", "avec": "con",
        "et": "y", "ou": "o", "sans": "sin", "sous": "bajo", "dans": "en", "en": "en",
        "cornichons": "pepinillos", "cornichon": "pepinillo", "vinaigre": "vinagre",
        "moutarde": "mostaza", "oignon": "cebolla", "échalotes": "chalotas",
        "ail": "ajo", "saumon": "salmón", "fumé": "ahumado", "fumée": "ahumada",
        "vins": "vinos", "vin": "vino", "balsamique": "balsámico", "rouge": "rojo",
        "blanc": "blanco", "naturel": "natural", "extra": "extra",
        "fines": "finas", "aigres": "agrios", "aigre": "agrio",
        "doux": "dulce", "douces": "dulces", "épices": "especias", "epices": "especias",
        "aromates": "aromáticas", "bocal": "frasco", "petites": "pequeñas",
        "artisanal": "artesano", "artisanale": "artesana", "traditionnel": "tradicional",
        "gros": "grande", "fins": "finos", "sucre": "azúcar", "sel": "sal", "eau": "agua",
        "mer": "mar", "olive": "oliva", "huile": "aceite", "tonne": "atún", "thon": "atún",
        "sardines": "sardinas", "anchois": "anchoas", "creme": "crema", "fromage": "queso",
        "lait": "leche", "yaourt": "yogur", "beurre": "mantequilla", 
        "confiture": "mermelada", "confitures": "mermeladas", "fruits": "frutas", "fruit": "fruta",
        "fraise": "fresa", "fraises": "fresas", "framboise": "frambuesa", "cerises": "cerezas",
        "abricot": "albaricoque", "pêche": "melocotón", "pruneau": "ciruela", "pomme": "manzana",
        "poire": "pera", "citron": "limón", "orange": "naranja", "mangue": "mango",
        "noix": "nuez", "amande": "almendra", "chocolat": "chocolate", "cacao": "cacao",
        "vanille": "vainilla", "cannelle": "canela", "romarin": "romero", "thym": "tomillo",
        "basilic": "albahaca", "menthe": "menta", "origan": "orégano", "poivre": "pimienta",
        "piment": "chile", "chili": "chile", "courgette": "calabacín", "aubergine": "berenjena",
        "carotte": "zanahoria", "carottes": "zanahorias", "oignons": "cebollas",
        "champignon": "champiñón", "champignons": "champiñones", "tomate": "tomate",
        "haricots": "frijoles", "pois": "guisantes", "riz": "arroz", "miel": "miel",
        "bio": "ecológico", "grecque": "griega", "mariné": "marinado",
        "grillées": "asadas", "conserves": "conservas", "conserve": "conserva",
        "légumes": "verduras", "purée": "puré", "soupe": "sopa",
        "pâtes": "pastas", "biscuits": "galletas", "pain": "pan", "farine": "harina",
        "recette": "receta", "paysanne": "campesina", "croquants": "crujientes",
        "original": "original", "maison": "de la casa", "à": "con", "échalote": "chalota",
        "l'échalote": "chalota", "français": "francés", "française": "francesa",
        "mini": "mini", "petits": "pequeños", "petit": "pequeño", "marinées": "marinadas",
        "grillés": "asados", "dorés": "dorados", "entier": "entero", "râpé": "rallado",
        "frais": "fresco", "fraîche": "fresca", "maigre": "magro", "salé": "salado",
    },
    "de": {
        "die": "", "das": "", "und": "y", "mit": "con", "im": "en", "in": "en",
        "von": "de", "ohne": "sin", "auf": "sobre", "für": "para",
        "gurken": "pepinillos", "gurke": "pepinillo", "sauerkraut": "chucrut",
        "rotkohl": "lombarda", "rot": "rojo", "grün": "verde", "schwarz": "negro",
        "weiß": "blanco", "weiss": "blanco", "knoblauch": "ajo", "zwiebeln": "cebollas",
        "zwiebel": "cebolla", "senf": "mostaza", "senfkörner": "granos de mostaza",
        "essig": "vinagre", "apfelessig": "vinagre de manzana", "milch": "leche",
        "käse": "queso", "kase": "queso", "wein": "vino", "bier": "cerveza",
        "apfel": "manzana", "äpfel": "manzanas", "zucker": "azúcar", "salz": "sal",
        "wasser": "agua", "öl": "aceite", "olivenöl": "aceite de oliva",
        "oliven": "aceitunas", "natur": "natural", "naturbelassen": "natural",
        "extra": "extra", "original": "original", "eingelegt": "encurtido",
        "eingelegte": "encurtidos", "süß": "dulce", "sauer": "agrio", "rauch": "ahumado",
        "geräuchert": "ahumado", "getrocknet": "seco", "gekocht": "cocido",
        "mariniert": "marinado", "scharf": "picante", "würzig": "especiado",
        "scheiben": "rodajas", "ganze": "enteros", "haus": "casa", "hausgemacht": "casero",
        "klassisch": "clásico", "traditionell": "tradicional", "biologisch": "ecológico",
        "aus": "de", "dem": "el", "der": "", "bio": "eco", "spreewald": "Spreewald",
        "feine": "finas", "fein": "fino", "geröstet": "tostado", "frisch": "fresco",
    },
    "it": {
        "il": "", "lo": "", "la": "", "i": "", "gli": "", "le": "", "un": "", "uno": "",
        "una": "", "del": "de", "della": "de", "di": "de", "con": "con", "e": "y", "o": "o",
        "in": "en", "senza": "sin", "sottaceti": "encurtidos", "sottaceto": "encurtido",
        "aceto": "vinagre", "vino": "vino", "tonno": "atún", 
        "acciuga": "anchoa", "sardine": "sardinas", "olive": "aceitunas", "oliva": "aceituna",
        "olio": "aceite", "senape": "mostaza", "cipolle": "cebollas", "cipolla": "cebolla",
        "aglio": "ajo", "peperoncino": "chile", "peperoncini": "chiles", "sale": "sal",
        "zucchero": "azúcar", "latte": "leche", "formaggio": "queso", "mozzarella": "mozzarella",
        "parmigiano": "parmesano", "stracchino": "stracchino", "yogurt": "yogur",
        "naturale": "natural", "biologico": "ecológico", "stagionato": "curado",
        "fresco": "fresco", "dolce": "dulce", "piccante": "picante", "affumicato": "ahumado",
        "essiccato": "seco", "agrodolce": "agridulce", "antipasto": "entrante",
        "melanzane": "berenjenas", "pomodoro": "tomate", "pomodori": "tomates",
        "carote": "zanahorias", "funghi": "champiñones", "basilico": "albahaca",
        "origano": "orégano", "peperoni": "pimientos", "zucchine": "calabacines",
        "pane": "pan", "alici": "anchoas", "acciughe": "anchoas",
    },
    "pt": {
        "o": "", "a": "", "os": "", "as": "", "um": "", "uma": "", "do": "de", "da": "de",
        "dos": "de", "das": "de", "de": "de", "com": "con", "e": "y", "em": "en",
        "sem": "sin", "pepino": "pepino", "pepinos": "pepinos", "cebola": "cebolla",
        "cebolas": "cebollas", "mostarda": "mostaza", "vinagre": "vinagre", "vinho": "vino",
        "queijo": "queso", "iogurte": "yogur", "leite": "leche", "manteiga": "mantequilla",
        "atum": "atún", "sardinhas": "sardinas", "anchovas": "anchoas", "azeitonas": "aceitunas",
        "azeite": "aceite", "sal": "sal", "açúcar": "azúcar", "agua": "agua", "água": "agua",
        "natural": "natural", "tradicional": "tradicional", "fresco": "fresco",
        "doce": "dulce", "picante": "picante", "fumado": "ahumado", "seco": "seco",
        "pimenta": "pimiento", "alho": "ajo", "tomate": "tomate", "tomates": "tomates",
        "couve": "col", "cenoura": "zanahoria", "cenouras": "zanahorias", "ervas": "hierbas",
        "folhas": "hojas", "abacaxi": "piña", "manga": "mango", "mel": "miel",
        "compota": "compota", "conserva": "conserva", "conservas": "conservas",
        "artesanal": "artesano", "biológico": "ecológico", "rústico": "rústico",
    },
    "pl": {
        "ogórki": "pepinillos", "ogórek": "pepinillo", "kapusta": "repollo",
        "kiszona": "fermentado", "kiszone": "encurtido", "czosnek": "ajo", "cebula": "cebolla",
        "musztarda": "mostaza", "ocet": "vinagre", "ser": "queso",
        "wino": "vino", "piwo": "cerveza", "sól": "sal", "cukier": "azúcar", "woda": "agua",
        "naturalny": "natural", "olej": "aceite", "oliwki": "aceitunas",
        "kislo": "agrio", "mleko": "leche",
        "duszona": "guisada", "grzyby": "setas", "wędzony": "ahumado",
        "twaróg": "requesón", "śmietana": "crema agria",
    },
    "nl": {
        "de": "", "het": "", "en": "y", "met": "con", "in": "en", "van": "de",
        "augurken": "pepinillos", "zuurkool": "chucrut", "mosterd": "mostaza",
        "azijn": "vinagre", "kaas": "queso", "melk": "leche", "bier": "cerveza",
        "wijn": "vino", "zoetzuur": "agridulce", "plakjes": "rodajas", "natuurlijk": "natural",
        "zout": "sal", "suiker": "azúcar", "water": "agua", "olijven": "aceitunas",
        "olijfolie": "aceite de oliva", "gerookt": "ahumado", "gekookt": "cocido",
    },
    "ru": {
        "бира": "cerveza", "кислые": "agrios", "кисели": "agrios",
        "краставички": "pepinillos", "огурцы": "pepinos", "нарезанные": "en rodajas",
        "нарязани": "en rodajas", "капуста": "repollo", "квашеная": "fermentada",
        "чеснок": "ajo", "уксус": "vinagre", "сыр": "queso", "молоко": "leche",
        "вино": "vino", "соль": "sal", "соус": "salsa", "вода": "agua",
    },
}

# Artículos que se eliminan al reconstruir el nombre.
_DROP_ARTICLES = {"the", "a", "an", "der", "die", "das", "le", "la", "les", "il", "lo", "gli", "i", "de", "het"}

_NOISE_RE = re.compile(r"^\s*\d+(?:[./-]\d+)*\s*(?:\(\d*\))?\s*\d*\s*")
_CITATION_RE = re.compile(r"\[\d+\]")
_WS_RE = re.compile(r"\s+")
_QTY_RE = re.compile(r"\s*\d+(?:[.,]\d+)?\s*(?:g|gr|ml|cl|l|kg)?\s*$", re.I)

# Sustantivos de producto que en español van al inicio ("X queso" -> "Queso X").
_CLASS_WORDS = {
    "queso", "cerveza", "vino", "sidra", "yogur", "kéfir", "té", "vinagre", "salsa",
    "mermelada", "chucrut", "pepinillos", "pepinillo", "pepino", "pan", "arroz", "atún",
    "anchoas", "anchoa", "sardinas", "sardina", "aceitunas", "aceituna", "caldo", "sopa",
    "pasta", "chocolate", "leche", "aceite", "alcaparras", "repollo", "remolacha",
    "cebolla", "cebollas", "ajo", "calabacín", "berenjena", "alcachofa", "mostaza",
    "pimiento", "pimientos", "limón", "fresa", "fresas", "miel", "agua", "puré",
    "conserva", "conservas", "encurtido", "encurtidos", "ahumado", "escabeche",
    "paté", "pâté", "terrine", "miso", "tempeh", "sake", "hidromiel",
    "crema", "zanahoria", "zanahorias", "rábano", "rábanos", "pescado", "pescados",
    "frijoles", "frijol", "gambas", "gamba", "mejillones", "manzana", "naranja",
    "melocotón", "ciruela", "albaricoque", "pera", "mango", "nuez", "almendra",
    "carne", "pato", "pollo", "cerdo", "cordero", "conejo", "trucha", "salmón",
    "arenque", "caballa",
}
_PREPS = {"de", "en", "con", "al", "del", "a", "la", "el", "un", "una", "y", "o"}
_NO_FRONT = {"lista", "listas", "list"}
_FUNCTION_WORDS = _PREPS | {"le", "les", "aux", "du", "des", "ou", "der", "die", "das", "mit",
                            "im", "aus", "von", "ohne", "het", "een", "van", "il", "lo", "gli",
                            "i", "uno", "una", "the", "and", "with", "of", "in", "for", "a", "an"}

_FEMININE = {
    "leche", "agua", "remolacha", "cebolla", "cebollas", "aceituna", "aceitunas",
    "sardina", "sardinas", "anchoa", "anchoas", "fresa", "fresas", "mermelada",
    "sopa", "carne", "col", "cerveza", "sidra", "mostaza", "alcachofa", "alcaparra",
    "alcaparras", "fruta", "frutas", "miel", "sal", "avena", "lombarda",
    "pasta", "pasta de soja", "harina", "crema", "zanahoria", "zanahorias",
    "naranja", "ciruela", "pera", "trucha", 
}

_ADJ_FEM = {
    "agrio": "agria", "seco": "seca", "ahumado": "ahumada", "fermentado": "fermentada",
    "encurtido": "encurtida", "negro": "negra", "blanco": "blanca", "rojo": "roja",
    "frito": "frita", "tostado": "tostada", "curado": "curada", "marinado": "marinada",
    "salado": "salada", "fresco": "fresca", "chino": "china", "italiano": "italiana",
    "griego": "griega", "coreano": "coreana", "suizo": "suiza", "picante": "picante",
    "dulce": "dulce", "natural": "natural", "verde": "verde",
}
_ADJ_PLURAL = {
    "agrio": "agrios", "agria": "agrias", "dulce": "dulces", "seco": "secos", "seca": "secas",
    "ahumado": "ahumados", "ahumada": "ahumadas", "fermentado": "fermentados",
    "fermentada": "fermentadas", "encurtido": "encurtidos", "encurtida": "encurtidas",
    "picante": "picantes", "natural": "naturales", "verde": "verdes", "negro": "negros",
    "negra": "negras", "blanco": "blancos", "blanca": "blancas", "rojo": "rojos",
    "roja": "rojas", "frito": "fritos", "frita": "fritas", "tostado": "tostados",
    "tostada": "tostadas", "curado": "curados", "curada": "curadas", "marinado": "marinados",
    "marinada": "marinadas", "salado": "salados", "salada": "saladas", "fresco": "frescos",
    "fresca": "frescas", "chino": "chinos", "china": "chinas", "japonés": "japoneses",
    "coreano": "coreanos", "coreana": "coreanas", "italiano": "italianos", "italiana": "italianas",
    "francés": "franceses", "alemán": "alemanes", "griego": "griegos", "griega": "griegas",
    "español": "españoles", "turco": "turcos", "indio": "indios", "tailandés": "tailandeses",
    "vietnamita": "vietnamitas", "marroquí": "marroquíes", "mexicano": "mexicanos",
    "suizo": "suizos", "suiza": "suizas", "neerlandés": "neerlandeses", "belga": "belgas",
    "portugués": "portugueses",
}


def _agree_adjectives(translated: list[str], fronted: bool) -> list[str]:
    if not fronted:
        return translated
    cls = translated[0].lower()
    if cls not in _FEMININE and not cls.endswith("s"):
        return translated
    result = list(translated)
    for idx in range(1, len(result)):
        low = result[idx].lower()
        if cls.endswith("s") and low in _ADJ_PLURAL:
            result[idx] = _ADJ_PLURAL[low]
        elif cls in _FEMININE and low in _ADJ_FEM:
            result[idx] = _ADJ_FEM[low]
    return result


def build_index(lang: str) -> tuple[dict[str, str], dict[str, str]]:
    phrases = {p: t for p, t in sorted(_PHRASES.get(lang, []), key=lambda x: -len(x[0].split()))}
    words = _WORDS.get(lang, {})
    return phrases, words


_WORD_RE_CACHE: dict[str, list[tuple[re.Pattern, str]]] = {}


def _word_patterns(lang: str) -> list[tuple[re.Pattern, str]]:
    if lang not in _WORD_RE_CACHE:
        _, words = build_index(lang)
        _WORD_RE_CACHE[lang] = [
            (re.compile(rf"\b{re.escape(w)}\b"), w) for w in words
        ]
    return _WORD_RE_CACHE[lang]


def detect_language(name: str) -> str | None:
    """Devuelve el idioma detectado o None si es español/proper noun."""
    lo = name.lower()
    if any("\u0400" <= c <= "\u04FF" for c in lo):
        return "ru"
    if re.search(r"[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af\u0e00-\u0e7f]", lo):
        return "other"
    scores: Counter[str] = Counter()
    for lang in _WORDS:
        phrases, _ = build_index(lang)
        for phrase in phrases:
            if phrase in lo:
                scores[lang] += phrase.count(" ") + 1
        for pattern, _word in _word_patterns(lang):
            if pattern.search(lo):
                scores[lang] += 1
    if not scores:
        return None
    best, best_score = scores.most_common(1)[0]
    if best_score <= 0:
        return None
    # Palabra-función suelta ("Ou", "La", ...) no se traduce.
    if len(lo.split()) == 1 and lo.strip(".") in _FUNCTION_WORDS:
        return None
    es = scores.get("es", 0)
    if best == "es" or (es and es >= best_score):
        return None
    # Requiere al menos 2 coincidencias, o cobertura completa del nombre.
    if best_score < 2 and not _fully_covered(lo, best):
        return None
    return best


def _fully_covered(text: str, lang: str) -> bool:
    _, words = build_index(lang)
    tokens = [t.strip(",.").lower() for t in text.split() if t.strip(",.")]
    if not tokens:
        return False
    return all(tok in words for tok in tokens)


def translate(name: str, lang: str) -> str:
    phrases, words = build_index(lang)
    name = name.replace("&", " y ")
    chunks = re.split(r"\s*,\s*", name)
    results = [_translate_chunk(chunk, phrases, words) for chunk in chunks]
    results = [r for r in results if r]
    if not results:
        return name
    text = ", ".join(results)
    text = _WS_RE.sub(" ", text).strip(" -")
    return text


def _translate_chunk(chunk: str, phrases: dict[str, str], words: dict[str, str]) -> str:
    tokens = chunk.split()
    out: list[str] = []
    n = len(tokens)
    i = 0
    while i < n:
        matched = False
        for length in range(3, 0, -1):
            if i + length > n:
                continue
            phrase = " ".join(tokens[i : i + length]).lower()
            if phrase in phrases:
                out.append(phrases[phrase])
                i += length
                matched = True
                break
        if matched:
            continue
        tok = tokens[i]
        lo = tok.lower().strip(".")
        out.append(words[lo] if lo in words else tok)
        i += 1
    flat: list[str] = []
    for item in out:
        flat.extend(item.split())
    translated = [t for t in flat if t.strip()]
    if not translated:
        return chunk
    # Fronting: si hay un sustantivo de producto (clase) que NO va precedido de una
    # preposición, muévelo al frente junto con lo que le sigue, dejando los
    # modificadores al final ("Emmental queso" -> "Queso Emmental",
    # "Yongfeng salsa de chile" -> "Salsa de chile Yongfeng",
    # pero "pepinillos en vinagre" se mantiene).
    fronted = False
    class_idx = None
    # No mover el sustantivo si la frase es un contenedor ("Lista de ..."),
    # donde el sustantivo contenedor debe quedarse al inicio.
    block = translated and translated[0].lower() in _NO_FRONT
    if not block:
        for i in range(len(translated) - 1, -1, -1):
            if translated[i].lower() in _CLASS_WORDS:
                prev = translated[i - 1].lower() if i > 0 else ""
                if prev not in _PREPS:
                    class_idx = i
                    break
    if class_idx is not None and class_idx > 0:
        translated = translated[class_idx:] + translated[:class_idx]
        fronted = True
    translated = _agree_adjectives(translated, fronted)
    # Capitaliza la primera palabra; el resto en minúscula salvo nombres propios.
    result: list[str] = []
    for idx, t in enumerate(translated):
        result.append(t if idx and t[0].isupper() else t.lower())
    if result:
        result[0] = result[0].capitalize()
    return " ".join(result)


def fix_noise(name: str) -> str:
    n = _NOISE_RE.sub("", name)
    n = _CITATION_RE.sub("", n)
    n = _QTY_RE.sub("", n)
    n = _WS_RE.sub(" ", n).strip(" -,")
    return n or name


def describe_numeric(name: str, categories: list[str], brand: str | None) -> str:
    if len(name) >= 8:
        base = categories[0] if categories else "Producto"
        return f"{base} {brand}".strip() if brand else f"{base} (sin marca)"
    if "fermento_alcoholico" in categories:
        return f"Cerveza {name}"
    base = categories[0] if categories else "Producto"
    return f"{base} {name}"


def main():
    parser = argparse.ArgumentParser(description="Normaliza nombres/descripciones de la base de datos")
    parser.add_argument("--dry-run", action="store_true", help="No escribe cambios")
    parser.add_argument("--limit", type=int, default=0, help="Limitar a N productos (0 = todos)")
    args = parser.parse_args()

    session = SessionLocal()
    stats = Counter()
    changed = []
    try:
        products = session.query(models.Product).order_by(models.Product.id).all()
        if args.limit:
            products = products[: args.limit]

        # Fase 1: calcular el nombre final de cada producto sin escribir nada.
        targets = {}
        for product in products:
            orig_name = product.name
            name = fix_noise(orig_name)

            categories = [c.code for c in product.categories]
            brand = None
            for a in product.aliases:
                if a.language is None:
                    brand = a.name
                    break

            lang = None
            if re.fullmatch(r"\d[\d ]*", name.strip()):
                new_name = describe_numeric(name.strip(), categories, brand)
                stats["barcode/numeric"] += 1
            else:
                lang = detect_language(name)
                if lang and lang != "other":
                    new_name = translate(name, lang)
                    if new_name != name:
                        stats[f"translate:{lang}"] += 1
                    else:
                        stats["untranslated"] += 1
                else:
                    new_name = name
                    if lang == "other":
                        stats["script-other"] += 1
                    elif lang is None:
                        stats["proper/es"] += 1

            new_name = _WS_RE.sub(" ", new_name).strip() or orig_name
            targets[product.id] = (product, new_name, lang)

        # Fase 2: resolver colisiones de nombre de forma determinista
        # (constraint único products.name), contando TODOS los targets,
        # pero solo se renombra con sufijo al producto que cambia.
        name_counts = Counter(t[1] for t in targets.values())
        for pid, (product, new_name, lang) in list(targets.items()):
            if name_counts[new_name] > 1 and new_name.lower() != product.name.lower():
                targets[pid] = (product, f"{new_name} (Variedad {pid})", lang)

        # Fase 3: aplicar cambios.
        for product, new_name, lang in targets.values():
            orig_name = product.name
            if new_name and new_name.lower() != orig_name.lower():
                if not args.dry_run:
                    product.name = new_name
                changed.append((product.id, orig_name, new_name, lang or ""))
            elif new_name.lower() == orig_name.lower() and new_name != orig_name and not args.dry_run:
                product.name = new_name
                stats["case/space"] += 1

            # Descripción: limpiar marcadores de cita [n].
            if product.description and _CITATION_RE.search(product.description):
                desc = _CITATION_RE.sub("", product.description)
                desc = _WS_RE.sub(" ", desc).strip()
                if desc != product.description:
                    if not args.dry_run:
                        product.description = desc or None
                    stats["desc-citations"] += 1

            # Alias con el nombre original y su idioma.
            if new_name and new_name.lower() != orig_name.lower() and not args.dry_run:
                alias_lang = lang or "orig"
                exists = any(a.name == orig_name and a.language == alias_lang for a in product.aliases)
                if not exists:
                    product.aliases.append(models.ProductAlias(name=orig_name, language=alias_lang))
                    stats["alias-added"] += 1
        if not args.dry_run:
            session.commit()
    finally:
        session.close()

    print(f"\nProductos revisados: {len(changed)} con cambio de nombre (+{stats['case/space']} de formato)")
    for key, value in stats.most_common():
        print(f"  {key}: {value}")
    if args.dry_run:
        for pid, old, new, lang in changed[:150]:
            print(f"  [{pid}] [{lang}] {old!r} -> {new!r}")

    if not args.dry_run:
        from ingest.loader import create_full_text_table

        create_full_text_table()
        print("FTS reconstruido.")


if __name__ == "__main__":
    main()
