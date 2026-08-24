"""Fuente eAmbrosia: registro oficial europeo de Indicaciones Geográficas (roadmap datos).

Descarga el registro completo vía API REST de la Comisión Europea y filtra a
las IGs alimentarias registradas cuyo capítulo arancelario corresponde a
productos fermentados o conservas tradicionales:

- 0403 yogur/kefir/buttermilk, 0406 quesos y cuajadas -> fermento_lactico
- 0210 carne salada/en salmuera/seca/ahumada, 1601 embutidos, 1604 pescado preparado -> curado_sal
- 2001 vegetales en vinagre -> encurtido_vinagre, 2005 vegetales preparados -> conserva_esterilizada, 2007 mermeladas -> conserva_azucar
- 2207 vinagres -> fermento_acetico

Se excluyen materias primas frescas (fruta, grano, aceite, café...) para no
repetir el problema de calidad que motivó excluir Open Food Facts.
"""

import json
from pathlib import Path

import httpx

EAMBROSIA_URL = "https://webgate.ec.europa.eu/eambrosia-api/api/v1/geographical-indications"
RAW_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "eambrosia.json"

# prefijo CN (4 dígitos) -> categoría interna
_CN_CATEGORY = {
    "0403": ["fermento_lactico"],
    "0406": ["fermento_lactico"],
    "0210": ["curado_sal"],
    "1601": ["curado_sal"],
    "1604": ["curado_sal"],
    "2001": ["encurtido_vinagre"],
    "2005": ["conserva_esterilizada"],
    "2007": ["conserva_azucar"],
    "2207": ["fermento_acetico"],
}

_GI_TYPE_ES = {"PDO": "Denominación de Origen Protegida (DOP)", "PGI": "Indicación Geográfica Protegida (IGP)", "GI": "Indicación Geográfica (IG)"}


def _chapter_codes(item: dict) -> set[str]:
    codes = set()
    for c in item.get("cnClassification") or []:
        text = str(c.get("cnText") or c.get("cnCode") or "")
        codes.add(text[:4])
    return codes


def _categories_for(item: dict) -> list[str]:
    found: list[str] = []
    for prefix in _chapter_codes(item):
        cat = _CN_CATEGORY.get(prefix)
        if cat and cat[0] not in found:
            found.extend(cat)
    return found


def _label_tail(item: dict) -> str:
    """Última parte legible de cnTranslation, p.ej. 'Cheese and curd'."""
    for c in item.get("cnClassification") or []:
        trans = str(c.get("cnTranslation") or "")
        parts = [p.strip() for p in trans.split("|")]
        tail = parts[-1] if len(parts) > 1 else ""
        if " - " in tail:
            tail = tail.split(" - ", 1)[1]
        if tail:
            return tail
    return ""


def _description(item: dict) -> str | None:
    names = [str(n).strip() for n in (item.get("protectedNames") or []) if str(n).strip()]
    if not names:
        return None
    gi_type = _GI_TYPE_ES.get(str(item.get("giType")), "Indicación Geográfica de la UE")
    year = str(item.get("euProtectionDate") or "")[:4]
    tail = _label_tail(item)
    parts = [f"{names[0]} es un producto con {gi_type}"]
    if tail:
        parts.append(f"(clase CN: {tail})")
    countries = item.get("countries") or []
    if countries:
        parts.append(f"de {'/'.join(countries)}")
    if year:
        parts.append(f", protegida en la UE desde {year}")
    return " ".join(parts)


def _countries(iso_codes: list[str]) -> list[dict]:
    import pycountry

    out = []
    for code in iso_codes:
        country = pycountry.countries.get(alpha_2=str(code).upper())
        if country:
            out.append({"name": country.name, "iso2": country.alpha_2, "role": "origin"})
    return out


def parse_items(items: list[dict]) -> list[dict]:
    """Convierte las IGs crudas al formato de registro interno."""
    from ingest.normalize import find_ingredients

    rows = []
    seen_names: set[str] = set()
    for item in items:
        if item.get("productType") != "FOOD" or item.get("status") != "registered":
            continue
        if not item.get("giIdentifier"):
            continue
        categories = _categories_for(item)
        if not categories:
            continue
        names = [str(n).strip() for n in (item.get("protectedNames") or []) if str(n).strip()]
        if not names:
            continue
        main = names[0]
        key = main.lower()
        if key in seen_names:
            continue
        seen_names.add(key)

        aliases = [{"name": n, "language": None} for n in names[1:]]
        refs = []
        instrument = item.get("legalInstrument") or {}
        if instrument.get("uri"):
            refs.append(
                {
                    "title": f"Reglamento CE de registro {item.get('fileNumber') or ''}".strip(),
                    "ref_type": "legal",
                    "url": instrument.get("uri"),
                    "doi": None,
                }
            )
        rows.append(
            {
                "name": main,
                "aliases": aliases,
                "description": _description(item),
                "method": None,
                "fermentation_time": None,
                "countries": _countries(item.get("countries") or []),
                "ingredients": find_ingredients(_label_tail(item)),
                "categories": categories,
                "references": refs,
                "source_tag": "eambrosia",
            }
        )
    return rows


def _load_rows() -> list[dict]:
    if not RAW_PATH.exists():
        resp = httpx.get(EAMBROSIA_URL, follow_redirects=True, timeout=120)
        resp.raise_for_status()
        RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
        RAW_PATH.write_text(resp.text, encoding="utf-8")
    items = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    return parse_items(items)


def load_source() -> list[dict]:
    return _load_rows()
