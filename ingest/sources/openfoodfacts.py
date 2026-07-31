import json
import time
from pathlib import Path

import httpx

from ingest.normalize import find_ingredients, normalize_name, resolve_country

OFF_API = "https://world.openfoodfacts.org/api/v2/search"
HEADERS = {"User-Agent": "conservas-world/0.1 (research database seed)"}
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "openfoodfacts"

# Categorías de Open Food Facts a scrapear (tag, tope de productos).
CATEGORIES = {
    "pickled-vegetables": 250,
    "sauerkraut": 150,
    "kimchi": 150,
    "miso": 150,
    "tempeh": 150,
    "natto": 100,
    "kombucha": 150,
    "fermented-milk-drinks": 250,
    "vinegars": 200,
    "soy-sauces": 200,
    "fish-sauces": 100,
    "jams": 200,
    "marmalades": 100,
    "candied-fruits": 80,
    "gherkins": 80,
    "capers": 60,
}

_CATEGORY_DEFAULT = {
    "pickled-vegetables": ["encurtido_fermentado"],
    "sauerkraut": ["encurtido_fermentado"],
    "kimchi": ["encurtido_fermentado"],
    "miso": ["fermento_koji"],
    "tempeh": ["fermento_koji"],
    "natto": ["fermento_lactico"],
    "kombucha": ["fermento_alcoholico"],
    "fermented-milk-drinks": ["fermento_lactico"],
    "vinegars": ["fermento_acetico"],
    "soy-sauces": ["fermento_koji"],
    "fish-sauces": ["fermento_lactico"],
    "jams": ["conserva_azucar"],
    "marmalades": ["conserva_azucar"],
    "candied-fruits": ["conserva_azucar"],
    "gherkins": ["encurtido_vinagre"],
    "capers": ["encurtido_vinagre"],
}

_TAG_MAP = (
    ("sauerkraut", "encurtido_fermentado"),
    ("kimchi", "encurtido_fermentado"),
    ("pickled", "encurtido_fermentado"),
    ("pickle", "encurtido_fermentado"),
    ("tsukemono", "encurtido_fermentado"),
    ("miso", "fermento_koji"),
    ("tempeh", "fermento_koji"),
    ("soy-sauce", "fermento_koji"),
    ("natto", "fermento_lactico"),
    ("kefir", "fermento_lactico"),
    ("yogurt", "fermento_lactico"),
    ("fermented-milk", "fermento_lactico"),
    ("fermented-fish", "fermento_lactico"),
    ("fish-sauce", "fermento_lactico"),
    ("cheese", "fermento_lactico"),
    ("kombucha", "fermento_alcoholico"),
    ("beer", "fermento_alcoholico"),
    ("wine", "fermento_alcoholico"),
    ("cider", "fermento_alcoholico"),
    ("vinegar", "fermento_acetico"),
    ("jam", "conserva_azucar"),
    ("marmalade", "conserva_azucar"),
    ("candied", "conserva_azucar"),
    ("compote", "conserva_azucar"),
    ("fruit-preserve", "conserva_azucar"),
    ("gherkin", "encurtido_vinagre"),
    ("cornichon", "encurtido_vinagre"),
    ("caper", "encurtido_vinagre"),
    ("escabeche", "encurtido_vinagre"),
)

_FIELDS = [
    "code",
    "product_name",
    "brands",
    "quantity",
    "ingredients_text",
    "ingredients_text_es",
    "ingredients_text_en",
    "categories_tags",
    "countries_tags",
]


def _fetch_page(tag: str, page: int, page_size: int = 50) -> list[dict]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{tag}.p{page}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))["products"]

    params = {
        "categories_tags": tag,
        "fields": ",".join(_FIELDS),
        "page_size": page_size,
        "page": page,
    }
    last_exc = None
    for attempt in range(4):
        try:
            with httpx.Client(timeout=60, headers=HEADERS) as client:
                resp = client.get(OFF_API, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    cache_path.write_text(json.dumps(data), encoding="utf-8")
                    return data.get("products", [])
                last_exc = RuntimeError(f"HTTP {resp.status_code}")
        except httpx.HTTPError as exc:
            last_exc = exc
        time.sleep(5 * (2**attempt))
    raise RuntimeError(f"No se pudo obtener {tag} página {page}: {last_exc}")


def _country_from_tag(tag: str) -> dict | None:
    name = tag.split(":")[-1].replace("-", " ")
    if name in {"world", "unknown", "xx"}:
        return None
    resolved = resolve_country(name)
    if resolved:
        resolved["role"] = "origin"
    return resolved


def _ingredients_text(product: dict) -> str | None:
    for key in ("ingredients_text_es", "ingredients_text_en", "ingredients_text"):
        value = str(product.get(key) or "").strip()
        if value and value.lower() not in {"", "none", "unknown"}:
            return value
    return None


def _categories(tags: list[str], default: list[str]) -> list[str]:
    codes = set(default)
    for tag in tags:
        t = tag.split(":")[-1]
        for key, code in _TAG_MAP:
            if key in t:
                codes.add(code)
    return sorted(codes)


def _fetch_category(tag: str, cap: int) -> list[dict]:
    products = []
    page = 1
    while len(products) < cap:
        batch = _fetch_page(tag, page)
        if not batch:
            break
        products.extend(batch)
        if len(batch) < 50:
            break
        page += 1
        time.sleep(1.0)
    return products[:cap]


def _parse_product(product: dict, tag: str, default_categories: list[str]) -> dict | None:
    name = str(product.get("product_name") or "").strip()
    if not name:
        return None
    brand = str(product.get("brands") or "").strip()
    ingredients_text = _ingredients_text(product)
    countries = []
    for ctag in product.get("countries_tags") or []:
        resolved = _country_from_tag(ctag)
        if resolved:
            countries.append(resolved)
    code = str(product.get("code") or "")
    categories = _categories(product.get("categories_tags") or [], default_categories)
    ingredients = find_ingredients(f"{name} {ingredients_text or ''}")
    return {
        "name": name,
        "aliases": [{"name": brand, "language": None}] if brand and normalize_name(brand) != normalize_name(name) else [],
        "description": ingredients_text,
        "method": None,
        "fermentation_time": None,
        "countries": countries,
        "ingredients": ingredients,
        "categories": categories,
        "references": (
            [
                {
                    "title": "Open Food Facts",
                    "ref_type": "web",
                    "url": f"https://world.openfoodfacts.org/product/{code}",
                    "doi": None,
                }
            ]
            if code
            else []
        ),
        "source_tag": "openfoodfacts",
    }


def load_source() -> list[dict]:
    records = []
    for tag, cap in CATEGORIES.items():
        print(f"  OFF {tag}: ", end="", flush=True)
        default = _CATEGORY_DEFAULT[tag]
        try:
            products = _fetch_category(tag, cap)
        except RuntimeError as exc:
            print(f"ERROR ({exc})")
            continue
        parsed = []
        seen = set()
        for product in products:
            record = _parse_product(product, tag, default)
            if record is None:
                continue
            key = normalize_name(record["name"])
            if key in seen:
                continue
            seen.add(key)
            parsed.append(record)
        print(len(parsed))
        records.extend(parsed)
    return records
