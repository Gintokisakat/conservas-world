"""Wikidata profundo: expansión SPARQL de familias de fermentos (roadmap datos).

A diferencia del módulo wikidata.py (listas de Wikipedia), este fuente consulta
el endpoint SPARQL para traer TODOS los ítems cuyos P31 (instancia de) caen
bajo familias raíz conocidas:

- Q10943   cheese
- Q6950796 fermented food
- Q3506176 fermented milk product

Trae etiquetas ES/EN, descripciones, país de origen (P495→P297) e imagen
(P18, convertida a URL de Wikimedia Commons).
"""

import json
from pathlib import Path

import httpx

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
RAW_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "wikidata_deep.json"
# Caché del resultado final (parseado + descripciones): la fase de
# enriquecimiento tarda minutos y no debe repetirse si el proceso muere.
PARSED_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "wikidata_deep_parsed.json"

QUERY_TEMPLATE = """
SELECT DISTINCT ?item ?labelEn ?labelEs ?iso2 ?imageFile WHERE {
  VALUES ?root { wd:%(root)s }
  ?item wdt:P31/wdt:P279* ?root .
  OPTIONAL { ?item wdt:P495 ?c . ?c wdt:P297 ?iso2 }
  OPTIONAL { ?item wdt:P18 ?imageFile }
  OPTIONAL { ?item rdfs:label ?labelEn FILTER(lang(?labelEn)='en') }
  OPTIONAL { ?item rdfs:label ?labelEs FILTER(lang(?labelEs)='es') }
}
LIMIT 20000
"""

ROOTS = ["Q10943", "Q6950796", "Q3506176"]

_USER_AGENT = "ConservasDelMundo/0.2 (https://github.com/Gintokisakat/conservas-world)"

# Apelaciones vinícolas (DOC/DOCG/AOC...): son etiquetas de región vinícola,
# no productos fermentados distinguibles; las excluimos por calidad.
_WINE_APPELLATION_RE = None  # compilada perezosa en _is_wine_appellation


def _is_wine_appellation(name: str, description: str | None) -> bool:
    import re

    global _WINE_APPELLATION_RE
    if _WINE_APPELLATION_RE is None:
        _WINE_APPELLATION_RE = re.compile(
            r"denominaci[oó]n de origen controlada|denominazione di origine|appellation d'origine"
            r"|controlled designation of origin|protected designa?tion of origin for wines",
            re.IGNORECASE,
        )
    if _WINE_APPELLATION_RE.search(description or ""):
        return True
    return bool(re.search(r"\b(DOCG?|AOC|AOP|DOQ?|DOCa?)\b\s*$", name.strip()))


def _category_for(root_qid: str | None, cls_labels: set[str]) -> str:
    blob = " ".join(cls_labels).lower()
    if root_qid in {"Q10943", "Q3506176"}:
        return "fermento_lactico"
    if any(k in blob for k in ("cheese", "fromage", "queso", "milk", "lait", "leche", "yogurt", "yoghurt", "kefir", "dairy")):
        return "fermento_lactico"
    if any(k in blob for k in ("soy", "soja", "miso", "koji", "soybean", "natto", "tempeh", "doenjang", "douchi")):
        return "fermento_koji"
    if any(k in blob for k in ("wine", "vino", "beer", "cerveza", "cider", "sidra", "beverage", "bebida", "drink", "whisky", "rum", "sake", "pulque", "kvass", "mead", "hidromiel")):
        return "fermento_alcoholico"
    if any(k in blob for k in ("vinegar", "vinagre", "kombucha", "acetic")):
        return "fermento_acetico"
    if any(k in blob for k in ("fish", "pescado", "seafood", "meat", "carne", "sausage", "embutido", "salami", "ham", "jamón")):
        return "curado_sal"
    if any(k in blob for k in ("vegetable", "verdura", "cabbage", "repollo", "pickle", "encurtido", "tea", "té", "kimchi", "sauerkraut", "chucrut", "olive", "aceituna", "fruit", "fruta")):
        return "encurtido_fermentado"
    return "otro"


def _image_url(file_name: str) -> str | None:
    name = str(file_name or "").strip()
    if not name:
        return None
    from urllib.parse import quote

    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(name)}?width=800"


def _countries(iso_codes: set[str]) -> list[dict]:
    import pycountry

    out = []
    for code in sorted(iso_codes):
        country = pycountry.countries.get(alpha_2=str(code).upper())
        if country:
            out.append({"name": country.name, "iso2": country.alpha_2, "role": "origin"})
    return out


def _val(x) -> str | None:
    """Extrae el valor plano de un binding SPARQL ({'value': ...}) o lo devuelve tal cual."""
    if isinstance(x, dict):
        v = x.get("value")
        return str(v) if v is not None else None
    return str(x) if x is not None else None


def parse_rows(rows: list[dict]) -> list[dict]:
    """Agrega filas SPARQL (una por combinación de optionales) en registros."""
    from ingest.normalize import find_ingredients

    items: dict[str, dict] = {}
    for row in rows:
        uri = _val(row.get("item")) or ""
        qid = uri.rsplit("/", 1)[-1]
        if not qid.startswith("Q"):
            continue
        entry = items.setdefault(
            qid,
            {"labels": {}, "descs": {}, "iso": set(), "cls": set(), "image": None, "root": None},
        )
        if not entry["root"] and isinstance(row.get("rootQid"), dict):
            entry["root"] = str(row["rootQid"].get("value"))
        for lang in ("en", "es"):
            val = _val(row.get(f"label{lang.capitalize()}"))
            if val and val.strip():
                entry["labels"][lang] = val.strip()
            val = _val(row.get(f"desc{lang.capitalize()}"))
            if val and val.strip():
                entry["descs"][lang] = val.strip()
        val = _val(row.get("iso2"))
        if val:
            entry["iso"].add(val)
        val = _val(row.get("clsLabel"))
        if val:
            entry["cls"].add(val)
        val = _val(row.get("imageFile"))
        if val and not entry["image"]:
            entry["image"] = _image_url(val)

    records = []
    seen: set[str] = set()
    for qid, entry in items.items():
        name = entry["labels"].get("es") or entry["labels"].get("en")
        if not name or len(name) < 3:
            continue
        description = entry["descs"].get("es") or entry["descs"].get("en")
        if _is_wine_appellation(name, description):
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        aliases = [
            {"name": lbl, "language": lang}
            for lang, lbl in entry["labels"].items()
            if lbl.lower() != key
        ]
        blob = set(entry["cls"]) | {name} | {entry["labels"].get("en", "")} | {description or ""}
        categories = [_category_for(entry["root"], blob)]
        records.append(
            {
                "_qid": qid,
                "name": name,
                "aliases": aliases,
                "description": description,
                "method": None,
                "fermentation_time": None,
                "countries": _countries(entry["iso"]),
                "ingredients": find_ingredients(" ".join(entry["cls"]) or name),
                "categories": categories,
                "references": [
                    {
                        "title": f"Wikidata {qid}",
                        "ref_type": "web",
                        "url": f"https://www.wikidata.org/wiki/{qid}",
                        "doi": None,
                    }
                ],
                "source_tag": "wikidata",
                "image_url": entry["image"],
            }
        )
    return records


def _fetch() -> list[dict]:
    all_rows: list[dict] = []
    for root in ROOTS:
        resp = httpx.get(
            SPARQL_ENDPOINT,
            params={"query": QUERY_TEMPLATE % {"root": root}, "format": "json"},
            headers={"User-Agent": _USER_AGENT, "Accept": "application/sparql-results+json"},
            timeout=300,
        )
        resp.raise_for_status()
        data = resp.json()
        for binding in data.get("results", {}).get("bindings", []):
            binding["rootQid"] = {"value": root}
            all_rows.append(binding)
    return all_rows


def _fetch_descriptions(qids: list[str]) -> dict[str, dict[str, str]]:
    """Etiquetas/descripciones por lotes de 50 vía wbgetentities."""
    out: dict[str, dict[str, str]] = {}
    api = "https://www.wikidata.org/w/api.php"
    for i in range(0, len(qids), 50):
        chunk = qids[i : i + 50]
        try:
            resp = httpx.get(
                api,
                params={
                    "action": "wbgetentities",
                    "ids": "|".join(chunk),
                    "props": "descriptions",
                    "languages": "es|en",
                    "format": "json",
                    "formatversion": "2",
                },
                headers={"User-Agent": _USER_AGENT},
                timeout=60,
            )
            resp.raise_for_status()
            entities = resp.json().get("entities", {})
        except Exception:
            continue
        for qid, entity in entities.items():
            descs = {
                lang: v["value"]
                for lang, v in (entity.get("descriptions") or {}).items()
                if v.get("value")
            }
            if descs:
                out[qid] = descs
    return out


def load_source() -> list[dict]:
    if PARSED_PATH.exists():
        return json.loads(PARSED_PATH.read_text(encoding="utf-8"))
    if RAW_PATH.exists():
        rows = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    else:
        rows = _fetch()
        RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
        RAW_PATH.write_text(json.dumps(rows), encoding="utf-8")
    records = parse_rows(rows)

    # Enriquecer descripciones faltantes por lotes (wbgetentities).
    missing = [r["_qid"] for r in records if not r["description"]]
    descs = _fetch_descriptions(missing) if missing else {}
    for record in records:
        qid = record.pop("_qid", None)
        if not record["description"] and qid in descs:
            d = descs[qid]
            record["description"] = d.get("es") or d.get("en")
    PARSED_PATH.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    return records
