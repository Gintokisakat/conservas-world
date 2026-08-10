import io
import json
import re
import time
from pathlib import Path

import httpx
import pandas as pd
from ingest.normalize import find_ingredients, infer_categories, resolve_country

API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "conservas-world/0.1 (research database seed)"}
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "wikipedia"

PAGES = {
    "fermented": "List of fermented foods",
    "pickled": "List of pickled foods",
    "yogurt": "List of yogurt-based dishes and beverages",
    "milk": "List of fermented milk products",
    "cheeses": "List of cheeses",
    "soy": "List of soy-based foods",
}

_FERMENTED_SOY_RE = re.compile(
    r"\b(miso|tempeh|natto|douchi|doubanjiang|doenjang|cheonggukjang|gochujang|"
    r"hoisin|kecap|soy sauce|soybean paste|soya sauce|shoyu|tamari|fermented tofu|"
    r"sufu|stinky tofu|kinema|hawaijar|oncom|meju|tauco|bekang|sergem|tungrymbai)\b",
    re.I,
)

_REF_RE = re.compile(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", re.S)
_ANNOTATED_RE = re.compile(r"\{\{annotated link\|([^|}]+)(?:\|([^}]+))?\}\}", re.I)
_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
_BULLET_DESC_RE = re.compile(r"^(.+?)\s*(?:–|-)\s*(.+)$")
_MARKUP_RE = re.compile(r"''+|\[\[[^\]]*\]\]|\{\{[^}]*\}\}")

_WIKI_STOPWORDS = {"see also", "references", "further reading", "external links", "notes"}


def _clean_wiki(text: str) -> str:
    if not text:
        return ""
    text = _REF_RE.sub("", text)
    text = _LINK_RE.sub(lambda m: m.group(2) or m.group(1), text)
    text = _MARKUP_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip(" ,;")


def _fetch(title: str, prop: str) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{re.sub(r'[^a-z0-9]+', '_', title.lower())}.{prop}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))["parse"]
    params = {
        "action": "parse",
        "page": title,
        "prop": prop,
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
    }
    with httpx.Client(timeout=60, headers=HEADERS) as client:
        for attempt in range(6):
            resp = client.get(API, params=params)
            if resp.status_code == 200:
                break
            if resp.status_code in {429, 500, 502, 503, 504}:
                print(
                    f"  [wikipedia] {resp.status_code} en intento {attempt + 1}, "
                    f"esperando {5 * (attempt + 1)}s ...",
                    flush=True,
                )
                time.sleep(5 * (attempt + 1))
                continue
            resp.raise_for_status()
        else:
            raise RuntimeError(f"No se pudo obtener {title} ({prop})")
        data = resp.json()
    cache_path.write_text(json.dumps(data), encoding="utf-8")
    return data["parse"]


def _resolve_origin(text: str) -> list[dict]:
    countries = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        resolved = resolve_country(line)
        if resolved:
            resolved["role"] = "origin"
            countries.append(resolved)
    return countries


def _build_record(
    name: str,
    description: str,
    origin_text: str,
    page: str,
    default_categories: list[str] | None = None,
    aliases: list[str] | None = None,
    extra_text: str = "",
) -> dict:
    text = " ".join(filter(None, [name, description, extra_text]))
    categories = infer_categories(text)
    if default_categories:
        inferred = [c for c in categories if c != "otro"]
        categories = sorted(set(inferred) | set(default_categories))
    return {
        "name": name,
        "aliases": [{"name": a, "language": "en"} for a in aliases or []],
        "description": description or None,
        "method": None,
        "fermentation_time": None,
        "countries": _resolve_origin(origin_text),
        "ingredients": find_ingredients(text),
        "categories": categories,
        "references": [
            {
                "title": f"Wikipedia: {PAGES[page]}",
                "ref_type": "web",
                "url": f"https://en.wikipedia.org/wiki/{PAGES[page].replace(' ', '_')}",
                "doi": None,
            }
        ],
        "source_tag": "wikipedia",
    }


def _parse_table_records(
    html: str,
    page: str,
    default_categories: list[str] | None = None,
) -> list[dict]:
    tables = pd.read_html(io.StringIO(html))
    records = []
    for table in tables:
        col_map = {}
        for col in table.columns:
            if isinstance(col, tuple):
                parts = [str(p) for p in col if str(p) not in {"nan", "None", ""}]
                flat = " | ".join(parts)
            else:
                flat = str(col)
            col_map[flat] = col
        flat = list(col_map)
        if not any("Name" in c for c in flat) or not any("Description" in c for c in flat):
            continue
        name_col = next(c for c in flat if "Name" in c)
        desc_col = next(c for c in flat if "Description" in c)
        origin_cols = [
            c
            for c in flat
            if any(k in c.lower() for k in ("origin", "region", "country"))
        ]
        for _, row in table.iterrows():
            name = _clean_wiki(str(row[col_map[name_col]] or ""))
            if not name or name.lower() in {"name", "image"}:
                continue
            description = _clean_wiki(str(row[col_map[desc_col]] or ""))
            origin_text = ""
            for origin_col in origin_cols:
                origin_text += str(row[col_map[origin_col]] or "") + "\n"
            records.append(
                _build_record(name, description, origin_text, page, default_categories)
            )
    return records


def _parse_bullet_records(
    wikitext: str, page: str, default_categories: list[str] | None = None
) -> list[dict]:
    records = []
    for line in wikitext.splitlines():
        line = line.strip()
        if not line.startswith("*"):
            continue
        body = line.lstrip("* ")
        if body.lower() in _WIKI_STOPWORDS:
            continue
        m = _BULLET_DESC_RE.match(body)
        description = ""
        if m:
            name_text, description = m.group(1), _clean_wiki(m.group(2))
        else:
            name_text = body
        name = _clean_wiki(name_text)
        if not name or not _LINK_RE.search(name_text):
            continue
        records.append(_build_record(name, description, "", page, default_categories))
    return records


def _parse_annotated_records(
    wikitext: str, page: str, default_categories: list[str] | None = None
) -> list[dict]:
    records = []
    for line in wikitext.splitlines():
        line = line.strip()
        if not line.startswith("*"):
            continue
        m = _ANNOTATED_RE.search(line)
        if not m:
            continue
        name = _clean_wiki(m.group(2) or m.group(1))
        if not name:
            continue
        categories = default_categories
        if categories and re.search(r"\b(vinegar|escabeche|achar|halab|pickle)\b", name, re.I):
            categories = ["encurtido_vinagre"]
        records.append(_build_record(name, "", "", page, categories))
    return records


def _parse_fermented_table() -> list[dict]:
    html = _fetch(PAGES["fermented"], "text")["text"]
    return _parse_table_records(html, "fermented")


def _parse_pickled_list() -> list[dict]:
    wikitext = _fetch(PAGES["pickled"], "wikitext")["wikitext"]
    return _parse_annotated_records(wikitext, "pickled", ["encurtido_fermentado"])


def _parse_yogurt_list() -> list[dict]:
    wikitext = _fetch(PAGES["yogurt"], "wikitext")["wikitext"]
    return _parse_bullet_records(wikitext, "yogurt", ["fermento_lactico"])


def _split_cell(cell) -> list[str]:
    if cell is None or (isinstance(cell, float) and cell != cell):
        return []
    parts = re.split(r"[;,\n|]+", str(cell))
    return [p for p in (_clean_wiki(x) for x in parts) if p]


def _parse_fermented_milk_records() -> list[dict]:
    html = _fetch(PAGES["milk"], "text")["text"]
    records = []
    for table in pd.read_html(io.StringIO(html)):
        col_map = {}
        for col in table.columns:
            if isinstance(col, tuple):
                parts = [str(p) for p in col if str(p) not in {"nan", "None", ""}]
                flat = " | ".join(parts)
            else:
                flat = str(col)
            col_map[flat] = col
        flat = list(col_map)
        if not any("Product" in c for c in flat):
            continue
        name_col = next(c for c in flat if "Product" in c)
        origin_cols = [c for c in flat if "origin" in c.lower() or "country" in c.lower()]
        desc_cols = [c for c in flat if "Description" in c]
        agent_cols = [c for c in flat if "Fermentation agent" in c]
        alias_cols = [c for c in flat if "Alternative names" in c]
        desc_col = col_map[desc_cols[0]] if desc_cols else None
        agent_col = col_map[agent_cols[0]] if agent_cols else None
        alias_col = col_map[alias_cols[0]] if alias_cols else None
        is_list = any(c.strip() == "Product(s)" for c in flat)
        for _, row in table.iterrows():
            origin_text = "\n".join(str(row[col_map[c]] or "") for c in origin_cols)
            names = (
                _split_cell(row[col_map[name_col]])
                if is_list
                else [str(row[col_map[name_col]] or "").strip()]
            )
            for name in names:
                if not name:
                    continue
                description = _clean_wiki(str(row[desc_col] or "")) if desc_col else ""
                agent = _clean_wiki(str(row[agent_col] or "")) if agent_col else ""
                aliases = _split_cell(row[alias_col]) if alias_col else []
                records.append(
                    _build_record(
                        name,
                        description,
                        origin_text,
                        "milk",
                        ["fermento_lactico"],
                        aliases=aliases,
                        extra_text=agent,
                    )
                )
    return records


def _parse_soy_records() -> list[dict]:
    wikitext = _fetch(PAGES["soy"], "wikitext")["wikitext"]
    records = []
    for line in wikitext.splitlines():
        line = line.strip()
        if not line.startswith("*"):
            continue
        body = line.lstrip("* ")
        if body.lower() in _WIKI_STOPWORDS:
            continue
        m = _ANNOTATED_RE.search(body)
        if m:
            name = _clean_wiki(m.group(2) or m.group(1))
            if not name:
                continue
            description = ""
        else:
            m = _BULLET_DESC_RE.match(body)
            description = ""
            if m:
                name_text, description = m.group(1), _clean_wiki(m.group(2))
            else:
                name_text = body
            name = _clean_wiki(name_text)
            if not name:
                continue
        if not (
            re.search(r"\bferment", description, re.I) or _FERMENTED_SOY_RE.search(name)
        ):
            continue
        records.append(_build_record(name, description, "", "soy", ["fermento_koji"]))
    return records


def load_source() -> list[dict]:
    records = _parse_fermented_table()
    records.extend(_parse_pickled_list())
    records.extend(_parse_yogurt_list())
    records.extend(_parse_fermented_milk_records())
    records.extend(
        _parse_table_records(_fetch(PAGES["cheeses"], "text")["text"], "cheeses", [
            "fermento_lactico"
        ])
    )
    records.extend(_parse_soy_records())
    return records
