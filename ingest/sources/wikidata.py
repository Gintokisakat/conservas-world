import json
import re
import time
from pathlib import Path

import httpx

from ingest.normalize import find_ingredients, infer_categories, resolve_country

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "conservas-world/0.1 (research database seed)"}
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "wikidata"
BATCH = 50
PACE_SECONDS = 2.0

CATEGORIES = {
    "en.wikipedia.org": {
        "Fermented foods": None,
        "Pickles": ["encurtido_fermentado"],
        "Kimchi": ["encurtido_fermentado"],
    },
    "es.wikipedia.org": {
        "Alimentos fermentados": None,
        "Encurtidos": ["encurtido_fermentado"],
        "Bebidas fermentadas": ["fermento_alcoholico"],
    },
}

_LANG_PREF = {"en.wikipedia.org": "en", "es.wikipedia.org": "es"}

_NOISE_NAME_RE = re.compile(
    r"\b(pickling|pickle lifter|demonstration|refrigerator|jangdokdae|"
    r"alimento fermentado|fermented food|pepinillo frito|fried pickle|"
    r"carne ahumada|smoked meat|fermentación|fermentation|elaboración|"
    r"homebrewing|cultivos? alimenticios|starter culture|casa de cerveza|"
    r"brewery|pastrami|gravlax|tataki|pájaro verde|encurtir)\b",
    re.I,
)

_last_request = {"t": 0.0}


def _pace():
    elapsed = time.monotonic() - _last_request["t"]
    if elapsed < PACE_SECONDS:
        time.sleep(PACE_SECONDS - elapsed)
    _last_request["t"] = time.monotonic()


def _get(url: str, params: dict) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=60, headers=HEADERS) as client:
        for attempt in range(6):
            _pace()
            try:
                resp = client.get(url, params=params)
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                print(
                    f"  [{url.split('/')[2]}] {type(exc).__name__} en intento {attempt + 1}, "
                    f"esperando {5 * (attempt + 1)}s ...",
                    flush=True,
                )
                time.sleep(5 * (attempt + 1))
                continue
            if resp.status_code == 200:
                return resp.json()
            print(
                f"  [{url.split('/')[2]}] {resp.status_code} en intento {attempt + 1}, "
                f"esperando {5 * (attempt + 1)}s ...",
                flush=True,
            )
            if resp.status_code in {429, 500, 502, 503, 504}:
                time.sleep(5 * (attempt + 1))
                continue
            resp.raise_for_status()
    raise RuntimeError(f"No se pudo obtener {url} con {params}")


def _cache(path: Path, fetch):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    data = fetch()
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


def _fetch_category(title: str, site: str) -> list[dict]:
    path = CACHE_DIR / f"{site.split('.')[0]}_{re.sub(r'[^a-z0-9]+', '_', title.lower())}.json"

    def fetch():
        return _get(
            f"https://{site}/w/api.php",
            {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{title}",
                "cmnamespace": "0",
                "cmlimit": "500",
                "format": "json",
            },
        )

    data = _cache(path, fetch)
    return data.get("query", {}).get("categorymembers", [])


def _fetch_wikibase_items(titles: list[str], site: str) -> dict[str, str]:
    mapping = {}
    for i in range(0, len(titles), BATCH):
        chunk = titles[i : i + BATCH]
        data = _get(
            f"https://{site}/w/api.php",
            {
                "action": "query",
                "prop": "pageprops",
                "ppprop": "wikibase_item",
                "titles": "|".join(chunk),
                "format": "json",
                "formatversion": "2",
            },
        )
        for page in data.get("query", {}).get("pages", []):
            qid = page.get("pageprops", {}).get("wikibase_item")
            if qid:
                mapping[page["title"]] = qid
    return mapping


def _fetch_entities(qids: list[str]) -> dict:
    entities = {}
    for i in range(0, len(qids), BATCH):
        chunk = qids[i : i + BATCH]
        data = _get(
            WIKIDATA_API,
            {
                "action": "wbgetentities",
                "ids": "|".join(chunk),
                "props": "labels|descriptions|claims",
                "languages": "en|es",
                "format": "json",
            },
        )
        entities.update(data.get("entities", {}))
    return entities


def _fetch_labels(qids: set[str]) -> dict[str, str]:
    labels = {}
    for i in range(0, len(qids), BATCH):
        chunk = sorted(qids)[i : i + BATCH]
        data = _get(
            WIKIDATA_API,
            {
                "action": "wbgetentities",
                "ids": "|".join(chunk),
                "props": "labels",
                "languages": "en",
                "format": "json",
            },
        )
        for qid, entity in data.get("entities", {}).items():
            label = entity.get("labels", {}).get("en", {}).get("value")
            if label:
                labels[qid] = label
    return labels


def _claim_qids(entity: dict, prop: str) -> set[str]:
    qids = set()
    for claim in entity.get("claims", {}).get(prop, []):
        try:
            value = claim["mainsnak"]["datavalue"]["value"]
            qids.add(value["id"])
        except (KeyError, TypeError):
            continue
    return qids


_FOOD_RE = re.compile(
    r"\b(food|dish|drink|beverage|condiment|sauce|pickle|cheese|yogurt|yoghurt|"
    r"dairy|dessert|snack|bread|pastry|soup|stew|fermented|cured|ingredient|spread|"
    r"appetizer|breakfast|beer|wine|cider|mead|spirit|liqueur|juice|vinegar|sausage|"
    r"soft drink|tea|coffee|alcoholic drink|fermented beverage)\b",
    re.I,
)


def _is_food(entity: dict, p31_labels: dict[str, str]) -> bool:
    p31 = _claim_qids(entity, "P31")
    if not p31:
        return True
    labels = [p31_labels.get(qid, "") for qid in p31]
    meaningful = [lbl for lbl in labels if lbl]
    if not meaningful:
        return True
    return any(_FOOD_RE.search(lbl) for lbl in meaningful)


def _entity_text(entity: dict, lang: str) -> str:
    other = "es" if lang == "en" else "en"
    return entity.get("labels", {}).get(lang, {}).get("value") or entity.get(
        "labels", {}
    ).get(other, {}).get("value", "")


def _entity_description(entity: dict, lang: str) -> str | None:
    other = "es" if lang == "en" else "en"
    desc = entity.get("descriptions", {}).get(lang) or entity.get("descriptions", {}).get(
        other
    )
    return desc.get("value") if desc else None


def _records_for_category(
    category: str,
    default_categories: list[str] | None,
    site: str,
    qid_by_title: dict[str, str],
    entities: dict,
    p31_labels: dict[str, str],
    p495_labels: dict[str, str],
) -> list[tuple[str, dict]]:
    records = []
    lang = _LANG_PREF[site]
    for title, qid in qid_by_title.items():
        entity = entities.get(qid)
        if not entity or not _is_food(entity, p31_labels):
            continue
        name = _entity_text(entity, lang)
        if not name or _NOISE_NAME_RE.search(name):
            continue
        description = _entity_description(entity, lang)
        text = f"{name} {description or ''}"
        categories = infer_categories(text)
        if default_categories:
            inferred = [c for c in categories if c != "otro"]
            categories = sorted(set(inferred) | set(default_categories))
        countries = []
        for qid_c in _claim_qids(entity, "P495"):
            label = p495_labels.get(qid_c)
            if not label:
                continue
            resolved = resolve_country(label)
            if resolved:
                resolved["role"] = "origin"
                countries.append(resolved)
        records.append(
            (
                qid,
                {
                    "name": name,
                    "aliases": [{"name": title, "language": lang}] if title != name else [],
                    "description": description,
                    "method": None,
                    "fermentation_time": None,
                    "countries": countries,
                    "ingredients": find_ingredients(text),
                    "categories": categories,
                    "references": [
                        {
                            "title": f"Wikidata: {name}",
                            "ref_type": "web",
                            "url": f"https://www.wikidata.org/wiki/{qid}",
                            "doi": None,
                        }
                    ],
                    "source_tag": "wikidata",
                },
            )
        )
    return records


def load_source() -> list[dict]:
    records = []
    seen_qids = set()
    for site, categories in CATEGORIES.items():
        for category, default_categories in categories.items():
            pages = _fetch_category(category, site)
            titles = [p["title"] for p in pages]
            qid_by_title = _fetch_wikibase_items(titles, site)
            qids = sorted({q for q in qid_by_title.values() if q})
            entities = _fetch_entities(qids)
            p31 = set()
            p495 = set()
            for entity in entities.values():
                p31 |= _claim_qids(entity, "P31")
                p495 |= _claim_qids(entity, "P495")
            p31_labels = _fetch_labels(p31)
            p495_labels = _fetch_labels(p495)
            for qid, record in _records_for_category(
                category,
                default_categories,
                site,
                qid_by_title,
                entities,
                p31_labels,
                p495_labels,
            ):
                if qid in seen_qids:
                    continue
                seen_qids.add(qid)
                records.append(record)
    return records
