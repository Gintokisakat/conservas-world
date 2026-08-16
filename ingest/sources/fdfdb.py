"""Fuente FDF-DB (Fermented Dairy Food Database) — roadmap 2.13.

Los productos se toman de la hoja maestra del suplemento de Zinno et al. 2022
(doi: 10.3390/nu14214581). Los metadatos ricos (país, PDO/GI, región,
características, microbiota) provienen de las hojas por país del mismo suplemento.
Solo se importan los productos con metadatos ricos; los que solo tienen nombre +
clasificación se omiten para no degradar la calidad.
"""

import io
import json
import re
import zipfile
from pathlib import Path

import pandas as pd
from ingest.normalize import extract_microbes, normalize_name, resolve_country

XLSX_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "fdfdb" / "FDF-DB_table_S1.xlsx"
)
WAYBACK_URL = "https://web.archive.org/web/2023/https://www.mdpi.com/article/10.3390/nu14214581/s1"
PAPER_DOI = "10.3390/nu14214581"
PAPER_TITLE = (
    "Fermented Dairy Food Database (FDF-DB): a user-friendly and searchable database "
    "of traditional fermented dairy foods and associated microbiomes"
)

_SHEETS = [
    "Spanish cheeses",
    "French cheeses",
    "Italian cheeses A-F",
    "Italian cheeses G-Z",
    "Irish cheeses",
]

_CLASSIFICATION_LABEL = {
    "cheese": "cheese",
    "fermented milk": "fermented milk",
    "yogurt": "yogurt",
}

_MILK_PATTERNS = [
    ("vaca", re.compile(r"\bcow'?s?\b", re.I)),
    ("oveja", re.compile(r"\b(sheep'?s?|ewe'?s?)\b", re.I)),
    ("cabra", re.compile(r"\bgoat'?s?\b", re.I)),
    ("búfala", re.compile(r"\b(buffalo|bufala)\b", re.I)),
    ("camella", re.compile(r"\bcamel'?s?\b", re.I)),
    ("yegua", re.compile(r"\bmare'?s?\b", re.I)),
    ("yak", re.compile(r"\byak'?s?\b", re.I)),
]

_TREATMENT_PATTERNS = [
    ("pasteurizada", re.compile(r"\bpasteuri[sz]ed\b", re.I)),
    ("leche cruda", re.compile(r"\braw\b", re.I)),
    ("termizada", re.compile(r"\bthermi[sz]ed\b", re.I)),
]

_RIPENING_PATTERNS = [
    ("curado", re.compile(r"\b(aged|cured|matured)\b", re.I)),
    ("fresco", re.compile(r"\bfresh\b", re.I)),
    ("blando", re.compile(r"\bsoft\b", re.I)),
    ("semiduro", re.compile(r"\bsemi[- ](soft|hard)\b", re.I)),
    ("duro", re.compile(r"\bhard\b", re.I)),
]

_COUNTRY_ES = {
    "Afghanistan": "Afganistán",
    "Algeria": "Argelia",
    "Armenia": "Armenia",
    "Azerbaijan": "Azerbaiyán",
    "Belarus": "Bielorrusia",
    "Bosnia and Herzegovina": "Bosnia y Herzegovina",
    "Bulgaria": "Bulgaria",
    "Burundi": "Burundi",
    "Denmark": "Dinamarca",
    "Dominican Republic": "República Dominicana",
    "Egypt": "Egipto",
    "Ethiopia": "Etiopía",
    "Finland": "Finlandia",
    "France": "Francia",
    "Georgia": "Georgia",
    "Germany": "Alemania",
    "Greece": "Grecia",
    "Hungary": "Hungría",
    "Iceland": "Islandia",
    "India": "India",
    "Indonesia": "Indonesia",
    "Iran, Islamic Republic of": "Irán",
    "Ireland": "Irlanda",
    "Italy": "Italia",
    "Jordan": "Jordania",
    "Kenya": "Kenia",
    "Latvia": "Letonia",
    "Lebanon": "Líbano",
    "Lithuania": "Lituania",
    "Mexico": "México",
    "Mongolia": "Mongolia",
    "Nepal": "Nepal",
    "Netherlands": "Países Bajos",
    "Nicaragua": "Nicaragua",
    "Norway": "Noruega",
    "Poland": "Polonia",
    "Romania": "Rumania",
    "Russian Federation": "Rusia",
    "Rwanda": "Ruanda",
    "Serbia": "Serbia",
    "Slovakia": "Eslovaquia",
    "Slovenia": "Eslovenia",
    "South Africa": "Sudáfrica",
    "Spain": "España",
    "Sudan": "Sudán",
    "Sweden": "Suecia",
    "Tanzania, United Republic of": "Tanzania",
    "Türkiye": "Turquía",
    "Ukraine": "Ucrania",
    "United States": "Estados Unidos",
    "Zambia": "Zambia",
    "Zimbabwe": "Zimbabue",
}


def _ensure_xlsx():
    if XLSX_PATH.exists():
        return
    import httpx

    XLSX_PATH.parent.mkdir(parents=True, exist_ok=True)
    resp = httpx.get(WAYBACK_URL, follow_redirects=True, timeout=120)
    resp.raise_for_status()
    if resp.content[:2] != b"PK":
        raise RuntimeError("La descarga de Wayback no devolvió un ZIP válido")
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        entry = next(n for n in zf.namelist() if n.endswith(".xlsx"))
        XLSX_PATH.write_bytes(zf.read(entry))


def _cell(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _load_master() -> dict[str, dict]:
    """Lista maestra: nombre normalizado -> {name, classification}."""
    df = pd.read_excel(XLSX_PATH, sheet_name="List of dairy products", header=1)
    out = {}
    for _, row in df.iterrows():
        name = _cell(row.get("Product name"))
        if not name:
            continue
        classification = _cell(row.get("Dairy product classification")).lower()
        out[normalize_name(name)] = {
            "name": name,
            "classification": _CLASSIFICATION_LABEL.get(classification, classification),
        }
    return out


def _load_rich_sheets() -> dict[str, dict]:
    """Metadatos ricos: nombre normalizado -> {country, region, pdo, characteristics, microbiota}."""
    out: dict[str, dict] = {}
    for sheet in _SHEETS:
        df = pd.read_excel(XLSX_PATH, sheet_name=sheet)
        for _, row in df.iterrows():
            name = _cell(row.get("Product name"))
            if not name:
                continue
            key = normalize_name(name)
            entry = out.setdefault(
                key,
                {
                    "name": name,
                    "country": "",
                    "region": "",
                    "pdo": False,
                    "characteristics": "",
                    "microbiota": "",
                },
            )
            if not entry["country"]:
                entry["country"] = _cell(row.get("country"))
            if not entry["region"]:
                entry["region"] = _cell(row.get("Region"))
            pdo = _cell(row.get("PDO")).lower()
            if pdo in ("yes", "igp"):
                entry["pdo"] = True
            if not entry["characteristics"]:
                entry["characteristics"] = _cell(row.get("Characteristics"))
            if not entry["microbiota"]:
                entry["microbiota"] = _cell(row.get("Microbiota composition"))
    df = pd.read_excel(XLSX_PATH, sheet_name="Fermented milks")
    for _, row in df.iterrows():
        name = _cell(row.get("Product name"))
        if not name:
            continue
        key = normalize_name(name)
        entry = out.setdefault(
            key,
            {
                "name": name,
                "country": "",
                "region": "",
                "pdo": False,
                "characteristics": "",
                "microbiota": "",
            },
        )
        if not entry["country"]:
            entry["country"] = _cell(row.get("country"))
        if not entry["region"]:
            entry["region"] = _cell(row.get("Region"))
        if not entry["characteristics"]:
            entry["characteristics"] = _cell(row.get("Characteristics"))
        if not entry["microbiota"]:
            entry["microbiota"] = _cell(row.get("Microbiota composition"))
    return out


def _parse_countries(raw: str) -> list[dict]:
    results = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        resolved = resolve_country(part)
        if resolved:
            resolved["role"] = "origin"
            results.append(resolved)
    return results


def _parse_milk_type(text: str) -> list[str]:
    found = [label for label, pattern in _MILK_PATTERNS if pattern.search(text)]
    return list(dict.fromkeys(found))


def _parse_treatment(text: str) -> str | None:
    for label, pattern in _TREATMENT_PATTERNS:
        if pattern.search(text):
            return label
    return None


def _parse_ripening(text: str) -> str | None:
    for label, pattern in _RIPENING_PATTERNS:
        if pattern.search(text):
            return label
    return None


def _microbiota_list(text: str) -> list[str]:
    names = set()
    for part in re.split(r"[;\n]+", text):
        for taxon in re.split(r",| and ", part):
            taxon = taxon.strip().strip(".")
            if not taxon or re.fullmatch(r"(yeast|yeasts|bacteria|bacterium|sp|spp)", taxon, re.I):
                continue
            names.add(taxon)
    return sorted(names)


def _build_description(classification: str, countries: list[str], region: str,
                       milk_type: list[str]) -> str:
    label = {
        "cheese": "Queso tradicional",
        "fermented milk": "Leche fermentada tradicional",
        "yogurt": "Yogur tradicional",
    }.get(classification, "Lácteo fermentado tradicional")
    parts = [label]
    if milk_type:
        parts.append("de leche de " + " y ".join(milk_type))
    country_es = [_COUNTRY_ES.get(c, c) for c in countries]
    parts.append("de " + ", ".join(country_es) if country_es else "")
    text = " ".join(parts).replace("  ", " ").strip().rstrip(".")
    return text + "."


def _load_rows() -> list[dict]:
    _ensure_xlsx()
    master = _load_master()
    rich = _load_rich_sheets()
    rows = []
    for key, master_info in master.items():
        meta = rich.get(key)
        if meta is None:
            continue
        countries = _parse_countries(meta["country"])
        milk_type = _parse_milk_type(meta["characteristics"])
        treatment = _parse_treatment(meta["characteristics"])
        ripening = _parse_ripening(meta["characteristics"])
        microbiota = _microbiota_list(meta["microbiota"])
        description = _build_description(
            master_info["classification"],
            [c["name"] for c in countries],
            meta["region"],
            milk_type,
        )
        rows.append(
            {
                "name": master_info["name"],
                "aliases": [],
                "description": description,
                "method": None,
                "fermentation_time": None,
                "countries": countries,
                "ingredients": [{"name": "milk", "category": "lacteo"}],
                "categories": ["fermento_lactico"],
                "microbes": extract_microbes(meta["microbiota"] or meta["characteristics"]),
                "references": [
                    {"title": PAPER_TITLE, "ref_type": "literature", "url": None, "doi": PAPER_DOI}
                ],
                "source_tag": "fdfdb",
                "_dairy": {
                    "name": master_info["name"],
                    "classification": master_info["classification"],
                    "country": meta["country"],
                    "region": meta["region"],
                    "milk_type": " ".join(milk_type) or None,
                    "treatment": treatment,
                    "ripening": ripening,
                    "microbiota": microbiota,
                    "geographical_indication": meta["pdo"],
                    "characteristics": meta["characteristics"] or None,
                },
            }
        )
    return rows


def load_source() -> list[dict]:
    return _load_rows()


def populate_dairy(session) -> int:
    """Vincula los metadatos FDF-DB (tabla dairy_ferments) a los productos ya
    persistidos, casando por nombre normalizado (tanto nuevos como existentes)."""
    from app.db import models
    from sqlalchemy import select

    rows = _load_rows()
    by_key = {normalize_name(r["name"]): r["_dairy"] for r in rows}

    products = session.execute(select(models.Product)).scalars().all()
    index: dict[str, models.Product] = {}
    for product in products:
        key = normalize_name(product.name)
        if key in by_key:
            index[key] = product

    updated = 0
    for key, dairy in by_key.items():
        product = index.get(key)
        if product is None:
            continue
        existing = session.execute(
            select(models.DairyFerment).where(
                models.DairyFerment.product_id == product.id
            )
        ).scalar_one_or_none()
        payload = {
            "name": dairy["name"],
            "classification": dairy["classification"],
            "country": dairy["country"] or None,
            "region": dairy["region"] or None,
            "milk_type": dairy["milk_type"],
            "treatment": dairy["treatment"],
            "ripening": dairy["ripening"],
            "microbiota_json": json.dumps(dairy["microbiota"], ensure_ascii=False)
            if dairy["microbiota"]
            else None,
            "geographical_indication": dairy["geographical_indication"],
            "characteristics": dairy["characteristics"],
        }
        if existing is None:
            session.add(models.DairyFerment(product_id=product.id, **payload))
            updated += 1
        else:
            changed = any(getattr(existing, k) != v for k, v in payload.items())
            if changed:
                for k, v in payload.items():
                    setattr(existing, k, v)
                updated += 1
    session.commit()
    return updated
