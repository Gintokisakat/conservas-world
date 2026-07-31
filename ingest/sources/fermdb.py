import re
from pathlib import Path

import pandas as pd

from ingest.normalize import (
    fermdb_categories,
    find_ingredients,
    resolve_country,
)

FERMDB_URL = "https://raw.githubusercontent.com/bokulich-lab/FermDB/main/FermDB_data.tsv"
RAW_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "FermDB_data.tsv"

_DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", re.IGNORECASE)


def _parse_references(reference: str, webpage: str) -> list[dict]:
    refs = []
    if reference and str(reference).strip():
        doi = _DOI_RE.search(reference)
        refs.append(
            {
                "title": str(reference).strip(),
                "ref_type": "literature",
                "url": None,
                "doi": doi.group(0) if doi else None,
            }
        )
    if webpage and str(webpage).strip():
        refs.append(
            {
                "title": "Wikipedia (referencia de FermDB)",
                "ref_type": "web",
                "url": str(webpage).strip(),
                "doi": None,
            }
        )
    return refs


def _parse_countries(country_cell: str) -> list[dict]:
    results = []
    for raw in country_cell.split(","):
        resolved = resolve_country(raw)
        if resolved:
            resolved["role"] = "origin"
            results.append(resolved)
    return results


def _parse_ingredients(row) -> list[dict]:
    raw = row.get("Raw material")
    if not raw or str(raw).strip() in {"nan", ""}:
        raw = row.get("Raw material ontology")
    return find_ingredients(str(raw or ""))


def _load_rows() -> list[dict]:
    if not RAW_PATH.exists():
        import httpx

        resp = httpx.get(FERMDB_URL, follow_redirects=True, timeout=60)
        resp.raise_for_status()
        RAW_PATH.write_text(resp.text, encoding="utf-8")
    df = pd.read_csv(RAW_PATH, sep="\t", dtype=str, keep_default_na=False)
    rows = []
    for _, row in df.iterrows():
        name = str(row.get("Product") or "").strip()
        if not name:
            continue
        countries = _parse_countries(str(row.get("Country") or ""))
        ingredients = _parse_ingredients(row)
        categories = fermdb_categories(str(row.get("Category") or ""))
        aliases = []
        original = str(row.get("Original Name") or "").strip()
        if original and original.lower() != name.lower():
            aliases.append({"name": original, "language": None})
        description = str(row.get("Description") or "").strip()
        refs = _parse_references(str(row.get("Reference") or ""), str(row.get("Webpage reference") or ""))
        rows.append(
            {
                "name": name,
                "aliases": aliases,
                "description": description or None,
                "method": None,
                "fermentation_time": None,
                "countries": countries,
                "ingredients": ingredients,
                "categories": categories,
                "references": refs,
                "source_tag": "fermdb",
            }
        )
    return rows


def load_source() -> list[dict]:
    return _load_rows()
