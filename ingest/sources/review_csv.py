"""Fuente de revisión curada: lee los CSV aprobados en review/ (include=yes).

Los CSV se generan/ajustan a mano según review/README.md; este módulo solo
consume las filas aprobadas y las convierte al formato de registro interno.
"""

import csv
import re
from pathlib import Path

from ingest.normalize import resolve_country

REVIEW_DIR = Path(__file__).resolve().parent.parent.parent / "review"

_VALID_CATEGORIES = {
    "fermento_lactico",
    "fermento_alcoholico",
    "fermento_acetico",
    "fermento_alcalino",
    "fermento_koji",
    "fermento_cereal",
    "encurtido_fermentado",
    "encurtido_vinagre",
    "encurtido_salmuera",
    "conserva_esterilizada",
    "conserva_azucar",
    "conserva_aceite",
    "curado_sal",
    "ahumado",
    "secado",
    "fermento_mixto",
    "otro",
}


def _countries(cell: str) -> list[dict]:
    """Resuelve 'Perú, Ecuador' / 'México (Chiapas)' a lista de países."""
    out: dict[str, dict] = {}
    extra_notes: list[str] = []
    for token in re.split(r"[,;/]|\by\b", cell or ""):
        token = token.strip()
        if not token:
            continue
        note = ""
        m = re.match(r"^(.*?)\s*\((.+)\)$", token)
        if m:
            token, note = m.group(1).strip(), f" ({m.group(2)})"
        resolved = resolve_country(token)
        if resolved:
            entry = {**resolved, "role": "origin"}
            if note:
                entry = {**entry, "name": entry["name"] + note}
            out[resolved["iso2"] or resolved["name"]] = entry
        else:
            extra_notes.append(token + note)
    countries = list(out.values())
    if extra_notes:
        for c in countries:
            c["name"] += " — " + "/".join(extra_notes)
            break
    return countries


def load_source() -> list[dict]:
    records: list[dict] = []
    seen: set[str] = set()
    for path in sorted(REVIEW_DIR.glob("*.csv")):
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                include = (row.get("include") or "").strip().lower()
                name = (row.get("name") or "").strip()
                if include != "yes" or len(name) < 3:
                    continue
                key = name.lower()
                if key in seen:
                    continue
                seen.add(key)
                category = (row.get("category") or "").strip().lower() or "otro"
                if category not in _VALID_CATEGORIES:
                    category = "otro"
                source_ref = (row.get("source_ref") or "").strip()
                records.append(
                    {
                        "name": name,
                        "aliases": [],
                        "description": (row.get("description_es") or "").strip() or None,
                        "method": None,
                        "fermentation_time": None,
                        "countries": _countries(row.get("country") or ""),
                        "ingredients": [],
                        "microbes": [],
                        "categories": [category],
                        "references": (
                            [
                                {
                                    "title": source_ref or "Revisión curada Conservas del Mundo",
                                    "ref_type": "literature",
                                    "url": None,
                                    "doi": None,
                                }
                            ]
                            if source_ref
                            else []
                        ),
                        "source_tag": "review",
                    }
                )
    return records
