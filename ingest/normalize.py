import re
import unicodedata

import pycountry

from ingest.categories import CATEGORY_BY_CODE
from ingest.ingredients import match_ingredients


def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", " ", name)
    return re.sub(r"\s+", " ", name).strip()


_COUNTRY_ALIASES = {
    "türkiye": "TR",
    "turkey": "TR",
    "iran (islamic republic of)": "IR",
    "iran": "IR",
    "republic of korea": "KR",
    "south korea": "KR",
    "korea": "KR",
    "czechia": "CZ",
    "czech republic": "CZ",
    "russian federation": "RU",
    "russia": "RU",
    "viet nam": "VN",
    "vietnam": "VN",
    "united republic of tanzania": "TZ",
    "tanzania": "TZ",
    "netherlands (kingdom of the)": "NL",
    "netherlands": "NL",
    "venezuela (bolivarian republic of)": "VE",
    "bolivia (plurinational state of)": "BO",
    "lao people's democratic republic": "LA",
    "laos": "LA",
    "côte d'ivoire": "CI",
    "cote d'ivoire": "CI",
    "state of palestine": "PS",
    "palestine": "PS",
    "syrian arab republic": "SY",
    "syria": "SY",
    "united kingdom of great britain and northern ireland": "GB",
    "united kingdom": "GB",
    "uk": "GB",
    "united states of america": "US",
    "usa": "US",
    "republic of moldova": "MD",
    "moldova": "MD",
    "north macedonia": "MK",
    "brunei darussalam": "BN",
    "brunei": "BN",
    "congo": "CG",
    "democratic republic of the congo": "CD",
    "eswatini": "SZ",
    "cabo verde": "CV",
    "gambia": "GM",
}

_REGION_TOKENS = {
    "worldwide",
    "global",
    "unknown",
    "mesoamerica",
    "eurasia",
    "asia",
    "europe",
    "africa",
    "north america",
    "south america",
    "oceania",
    "atlantic ocean",
    "caribbean",
    "central america",
    "east asia",
    "southeast asia",
    "south asia",
    "central asia",
    "west africa",
    "east africa",
    "eastern africa",
    "northern europe",
    "eastern europe",
    "southern europe",
    "western europe",
    "nordic countries",
    "mediterranean",
    "caucasus",
    "indian subcontinent",
    "baltic",
    "polynesia",
    "melanesia",
    "micronesia",
}


def _build_country_index():
    index = {}
    for country in pycountry.countries:
        variants = [country.name]
        if getattr(country, "official_name", None):
            variants.append(country.official_name)
        if getattr(country, "common_name", None):
            variants.append(country.common_name)
        for v in variants:
            key = normalize_name(v)
            if key not in index:
                index[key] = country
    return index


_COUNTRY_INDEX = _build_country_index()

_CONTINENT_BY_ISO2 = {
    "DZ": "Africa", "AO": "Africa", "BJ": "Africa", "BW": "Africa", "BF": "Africa",
    "BI": "Africa", "CV": "Africa", "CM": "Africa", "CF": "Africa", "TD": "Africa",
    "KM": "Africa", "CG": "Africa", "CD": "Africa", "CI": "Africa", "DJ": "Africa",
    "EG": "Africa", "GQ": "Africa", "ER": "Africa", "SZ": "Africa", "ET": "Africa",
    "GA": "Africa", "GM": "Africa", "GH": "Africa", "GN": "Africa", "GW": "Africa",
    "KE": "Africa", "LS": "Africa", "LR": "Africa", "LY": "Africa", "MG": "Africa",
    "MW": "Africa", "ML": "Africa", "MR": "Africa", "MU": "Africa", "MA": "Africa",
    "MZ": "Africa", "NA": "Africa", "NE": "Africa", "NG": "Africa", "RW": "Africa",
    "ST": "Africa", "SN": "Africa", "SC": "Africa", "SL": "Africa", "SO": "Africa",
    "ZA": "Africa", "SS": "Africa", "SD": "Africa", "TZ": "Africa", "TG": "Africa",
    "TN": "Africa", "UG": "Africa", "EH": "Africa", "ZM": "Africa", "ZW": "Africa",
    "AG": "Americas", "AR": "Americas", "BS": "Americas", "BB": "Americas", "BZ": "Americas",
    "BO": "Americas", "BR": "Americas", "CA": "Americas", "CL": "Americas", "CO": "Americas",
    "CR": "Americas", "CU": "Americas", "DM": "Americas", "DO": "Americas", "EC": "Americas",
    "SV": "Americas", "GD": "Americas", "GT": "Americas", "GY": "Americas", "HT": "Americas",
    "HN": "Americas", "JM": "Americas", "MX": "Americas", "NI": "Americas", "PA": "Americas",
    "PY": "Americas", "PE": "Americas", "KN": "Americas", "LC": "Americas", "VC": "Americas",
    "SR": "Americas", "TT": "Americas", "US": "Americas", "UY": "Americas", "VE": "Americas",
    "AF": "Asia", "AM": "Asia", "AZ": "Asia", "BH": "Asia", "BD": "Asia", "BT": "Asia",
    "BN": "Asia", "KH": "Asia", "CN": "Asia", "CY": "Asia", "GE": "Asia", "IN": "Asia",
    "ID": "Asia", "IR": "Asia", "IQ": "Asia", "IL": "Asia", "JP": "Asia", "JO": "Asia",
    "KZ": "Asia", "KW": "Asia", "KG": "Asia", "LA": "Asia", "LB": "Asia", "MY": "Asia",
    "MV": "Asia", "MN": "Asia", "MM": "Asia", "NP": "Asia", "OM": "Asia", "PK": "Asia",
    "PS": "Asia", "PH": "Asia", "QA": "Asia", "SA": "Asia", "SG": "Asia", "LK": "Asia",
    "SY": "Asia", "TJ": "Asia", "TH": "Asia", "TL": "Asia", "TR": "Asia", "TM": "Asia",
    "AE": "Asia", "UZ": "Asia", "VN": "Asia", "YE": "Asia", "KR": "Asia", "KP": "Asia",
    "TW": "Asia", "HK": "Asia", "MO": "Asia",
    "AL": "Europe", "AD": "Europe", "AT": "Europe", "BY": "Europe", "BE": "Europe",
    "BA": "Europe", "BG": "Europe", "HR": "Europe", "CZ": "Europe", "DK": "Europe",
    "EE": "Europe", "FI": "Europe", "FR": "Europe", "DE": "Europe", "GR": "Europe",
    "HU": "Europe", "IS": "Europe", "IE": "Europe", "IT": "Europe", "XK": "Europe",
    "LV": "Europe", "LI": "Europe", "LT": "Europe", "LU": "Europe", "MT": "Europe",
    "MD": "Europe", "MC": "Europe", "ME": "Europe", "NL": "Europe", "MK": "Europe",
    "NO": "Europe", "PL": "Europe", "PT": "Europe", "RO": "Europe", "RU": "Europe",
    "SM": "Europe", "RS": "Europe", "SK": "Europe", "SI": "Europe", "ES": "Europe",
    "SE": "Europe", "CH": "Europe", "UA": "Europe", "GB": "Europe", "VA": "Europe",
    "AU": "Oceania", "FJ": "Oceania", "KI": "Oceania", "MH": "Oceania", "FM": "Oceania",
    "NR": "Oceania", "NZ": "Oceania", "PW": "Oceania", "PG": "Oceania", "WS": "Oceania",
    "SB": "Oceania", "TO": "Oceania", "TV": "Oceania", "VU": "Oceania", "PF": "Oceania",
    "AQ": "Antarctica", "GL": "Americas",
    "IM": "Europe", "MQ": "Americas", "RE": "Africa",
}


def resolve_country(name: str) -> dict | None:
    raw = name.strip()
    key = normalize_name(raw)
    if not key:
        return None
    if key in _REGION_TOKENS:
        return None
    iso2 = _COUNTRY_ALIASES.get(key)
    country = None
    if iso2:
        country = pycountry.countries.get(alpha_2=iso2)
    if country is None:
        country = _COUNTRY_INDEX.get(key)
    if country is None:
        country = _country_inside(key)
    if country is None:
        return None
    continent = _CONTINENT_BY_ISO2.get(country.alpha_2)
    return {
        "name": country.name,
        "iso2": country.alpha_2,
        "iso3": country.alpha_3,
        "continent": continent,
    }


_COUNTRY_BY_LENGTH = sorted(_COUNTRY_INDEX.items(), key=lambda kv: -len(kv[0]))


def _country_inside(key: str):
    for name, country in _COUNTRY_BY_LENGTH:
        if re.search(rf"\b{name}\b", key):
            return country
    return None


_INGREDIENT_RULES = [
    ("pescado", re.compile(r"\b(fish|anchov|herring|sardine|salmon|tuna|mackerel|cod|shark|trout|roe|fish sauce|fish paste|tilapia|catfish|mackerel)\b")),
    ("marisco", re.compile(r"\b(shrimp|prawn|crab|oyster|mussel|squid|clam|shellfish|sea urchin|sea cucumber|krill|fish roe)\b")),
    ("lacteo", re.compile(r"\b(milk|cheese|whey|butter|cream|yoghurt|yogurt|dairy|curd|kefir)\b")),
    ("carne", re.compile(r"\b(meat|pork|beef|chicken|mutton|lamb|goat meat|buffalo|sausage|ham|bacon|duck)\b")),
    ("legumbre", re.compile(r"\b(soy[a-z]*|bean|pea|lentil|chickpea|natto|miso|tofu|groundnut|peanut)\b")),
    ("cereal", re.compile(r"\b(rice|wheat|barley|oat|rye|millet|sorghum|maize|corn|buckwheat|teff|fonio|flour|bread|bran)\b")),
    ("raiz", re.compile(r"\b(cassava|potato|sweet potato|yam|taro|manioc|tapioca|root)\b")),
    ("fruta", re.compile(r"\b(fruit|apple|grape|mango|plum|banana|papaya|pineapple|lemon|orange|date|fig|coconut|durian|berry|berries|jujube|pomegranate|persimmon|elderberry|gooseberry|peach|apricot)\b")),
    ("vegetal", re.compile(r"\b(cabbage|cucumber|radish|carrot|garlic|onion|ginger|pepper|chili|chilli|mushroom|bamboo|mustard|turnip|beet|beetroot|cauliflower|eggplant|okra|olive|artichoke|spinach|leaf|leaves|greens|vegetable|tomato|pumpkin|squash|celery|daikon)\b")),
    ("hongo", re.compile(r"\b(mushroom|koji|mold|mould|tempeh|fungus|yeast)\b")),
    ("bebida", re.compile(r"\b(tea|coffee|cacao|cocoa|wine|vinegar|juice|cane|sugarcane|sugar|honey|molasses|toddy|palm sap)\b")),
]


def categorize_ingredient(name: str) -> str | None:
    text = name.lower()
    for category, pattern in _INGREDIENT_RULES:
        if pattern.search(text):
            return category
    return None


def find_ingredients(text: str) -> list[dict]:
    return match_ingredients(text)


def split_materials(raw: str | None) -> list[str]:
    if not raw or not str(raw).strip():
        return []
    parts = [p.strip() for p in str(raw).split(",")]
    parts = [re.sub(r"^\W+|\W+$", "", p) for p in parts]
    return [p for p in parts if p]


FERMDB_CATEGORY_MAP = {
    "acid beverage": ["fermento_lactico"],
    "alcoholic beverage": ["fermento_alcoholico"],
    "beer": ["fermento_alcoholico"],
    "cheese": ["fermento_lactico"],
    "dairy product": ["fermento_lactico"],
    "fermented cereal": ["fermento_lactico"],
    "fermented fish": ["fermento_lactico"],
    "fermented fruit": ["fermento_alcoholico"],
    "fermented legumes": ["fermento_koji", "fermento_lactico"],
    "fermented meat": ["fermento_lactico"],
    "fermented roots": ["fermento_lactico"],
    "fermented vegetables": ["fermento_lactico"],
    "wine": ["fermento_alcoholico"],
    "yogurt": ["fermento_lactico"],
}


def fermdb_categories(fermdb_category: str) -> list[str]:
    codes = FERMDB_CATEGORY_MAP.get(fermdb_category.strip().lower(), ["fermento_mixto"])
    return [c for c in codes if c in CATEGORY_BY_CODE]


def infer_categories(text: str) -> list[str]:
    t = "".join(
        c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c)
    )
    codes = set()
    if re.search(r"\b(wine|beer|alcohol|pulque|kombucha|vine beverage)\b", t):
        codes.add("fermento_alcoholico")
    if re.search(
        r"\b(water kefir|tibicos|ginger beer plant|scoby|symbiotic|mixed culture|sourdough)\b",
        t,
    ):
        codes.add("fermento_mixto")
    if re.search(r"\bvinegar\b", t):
        codes.add("fermento_acetico")
    if re.search(r"\b(koji|mold|mould|tempeh|miso|soy sauce|soya sauce|shoyu|tamari)\b", t):
        codes.add("fermento_koji")
    if re.search(
        r"\b(fermented|fermentation|sauerkraut|kimchi|kraut|brine|salmuera|"
        r"cheese|yogurt|yoghurt|sour cream|smetana|tvorog|kefir|buttermilk|sourdough|curd|"
        r"creme fraiche|fraiche)\b",
        t,
    ):
        codes.add("fermento_lactico")
    if re.search(r"\b(pickled|encurtido|pickle)\b", t):
        if re.search(r"\bvinegar\b", t):
            codes.add("encurtido_vinagre")
        else:
            codes.add("encurtido_fermentado")
    if re.search(r"\b(preserved|preserve|mermelada|jam|syrup|almibar|conserva)\b", t):
        codes.add("conserva_azucar")
    if not codes:
        return ["otro"]
    return sorted(codes)


_MICROBE_GENERA = (
    "Lactobacillus",
    "Lactococcus",
    "Leuconostoc",
    "Pediococcus",
    "Streptococcus",
    "Oenococcus",
    "Enterococcus",
    "Bifidobacterium",
    "Propionibacterium",
    "Brevibacterium",
    "Halanaerobium",
    "Staphylococcus",
    "Micrococcus",
    "Bacillus",
    "Clostridium",
    "Acetobacter",
    "Gluconobacter",
    "Saccharomyces",
    "Saccharomycopsis",
    "Schizosaccharomyces",
    "Pichia",
    "Kluyveromyces",
    "Candida",
    "Debaryomyces",
    "Zygosaccharomyces",
    "Torulaspora",
    "Geotrichum",
    "Aspergillus",
    "Rhizopus",
    "Mucor",
    "Penicillium",
    "Monascus",
    "Neurospora",
    "Tetragenococcus",
    "Weissella",
    "Fusarium",
    "Actinomucor",
    "Propionibacterium",
)

_MICROBE_SPECIES_RE = re.compile(
    rf"\b({'|'.join(re.escape(g) for g in _MICROBE_GENERA)})(?:s|es)?\s+([a-z]{{3,}})",
    re.I,
)

# Palabras que no son especies válidas (falsos positivos).
_MICROBE_STOPWORDS = {
    "bacteria",
    "bacterium",
    "species",
    "spp",
    "sp",
    "strain",
    "strains",
    "culture",
    "cultures",
    "starters",
    "starterkultur",
    "starter",
    "organisms",
    "microbes",
    "cells",
    "found",
    "including",
    "in",
    "fermented",
    "ferment",
    "mold",
    "mould",
}

# Erratas de especies capturadas del texto fuente.
_MICROBE_FIXES = {
    "rhamnossus": "rhamnosus",
    "orizae": "oryzae",
    "coaguland": "coagulans",
    "thermophils": "thermophilus",
    "asei": "casei",
}


def _format_microbe(genus: str, species: str) -> str:
    clean = []
    for part in species.split():
        if part == "." or part.lower() in _MICROBE_STOPWORDS:
            continue
        clean.append(_MICROBE_FIXES.get(part.lower(), part))
    return f"{genus} {' '.join(clean)}" if clean else genus


def _canonical_genus(name: str) -> str:
    return next(g for g in _MICROBE_GENERA if g.lower() == name.lower())


def extract_microbes(text: str | None) -> list[str]:
    if not text:
        return []
    t = text.lower()
    found = []
    matched = set()
    for match in _MICROBE_SPECIES_RE.finditer(t):
        genus = _canonical_genus(match.group(1))
        name = _format_microbe(genus, match.group(2))
        found.append(name)
        matched.add(genus.lower())
    for genus in _MICROBE_GENERA:
        if re.search(rf"\b{genus.lower()}\b", t) and genus.lower() not in matched:
            found.append(genus)
    return list(dict.fromkeys(found))
