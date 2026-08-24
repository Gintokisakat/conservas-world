"""Fuente FAO 1998 — *Fermented fruits and vegetables: A global perspective*.

Extrae la Tabla 2.1 ("Fermented foods from around the world") del capítulo 2
del manual de la FAO (Battcock & Azam-Ali), organizada por región:
nombre(s) separados por comas y tipo de producto. Los tipos se mapean a la
taxonomía interna; los genéricos sin producto concreto (levaduras, vinos
inespecíficos) se excluyen.
"""

from pathlib import Path

import httpx
from lxml import html

FAO_CH2_URL = "https://www.fao.org/4/x0560e/x0560e07.htm"
RAW_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "fao_x0560e07.htm"

REGIONS = {
    "indian sub-continent": "el subcontinente indio",
    "south east asia": "el Sudeste Asiático",
    "east asia": "Este Asia",
    "africa": "África",
    "americas": "las Américas",
    "middle east": "Medio Oriente",
    "europe and world": "Europa y el mundo",
}

# Tipos de la tabla -> categoría interna
TYPE_CATEGORY = {
    "pickled fruit and vegetables": "encurtido_fermentado",
    "fermented dried vegetable": "encurtido_fermentado",
    "fermented tea leaves": "encurtido_fermentado",
    "pickled oilseed": "encurtido_fermentado",
    "fermented fruit and vegetables": "encurtido_fermentado",
    "fermented in brine": "encurtido_salmuera",
    "fermented fruit juice": "fermento_acetico",  # nata de coco/piña (Acetobacter)
    "vinegar": "fermento_acetico",
    "fermented fruit and vegetable seeds": "fermento_alcalino",
    "fermented fruits": "fermento_alcoholico",
}

# Filas genéricas sin producto concreto que no aportan valor
SKIP_NAMES = {
    "wines",
    "wine",
    "mushrooms",
    "yeast",
    "oilseeds",
    "vanilla",
    "citron",
    "olives",
}

_TYPE_ES = {
    "pickled fruit and vegetables": "frutas y verduras encurtidas",
    "fermented dried vegetable": "vegetal fermentado y secado",
    "fermented tea leaves": "hojas de té fermentadas",
    "pickled oilseed": "semillas encurtidas",
    "fermented fruit and vegetables": "frutas y verduras fermentadas",
    "fermented in brine": "fermentado en salmuera",
    "fermented fruit juice": "jugo de fruta fermentado",
    "vinegar": "vinagre",
    "fermented fruit and vegetable seeds": "semillas fermentadas alcalinas",
    "fermented fruits": "frutas fermentadas",
}


def _norm(text: str) -> str:
    return " ".join(str(text).split()).strip()


def parse_table(rows: list[list[str]]) -> list[dict]:
    """Convierte filas [nombres, tipo] en registros internos."""
    records: list[dict] = []
    seen: set[str] = set()
    region_key = ""
    last_type = ""
    for cells in rows:
        if len(cells) < 2:
            continue
        left, right = _norm(cells[0]), _norm(cells[1])
        if not left or left.lower() == "name and region" or left.lower() == "contents - previous - next":
            continue
        if left.lower() in REGIONS and not right:
            region_key = left.lower()
            continue
        ftype = right.lower() or last_type
        last_type = ftype
        category = TYPE_CATEGORY.get(ftype)
        if category is None:
            continue
        for raw_name in left.split(","):
            name = raw_name.strip()
            key = name.lower()
            if not name or key in SKIP_NAMES or key in seen or len(name) < 3:
                continue
            seen.add(key)
            type_es = _TYPE_ES.get(ftype, ftype)
            description = (
                f"{name} es un producto de fermentación tradicional de {REGIONS[region_key]}, "
                f"clasificado por la FAO (1998) como {type_es}."
                if region_key
                else None
            )
            records.append(
                {
                    "name": name,
                    "aliases": [],
                    "description": description,
                    "method": None,
                    "fermentation_time": None,
                    "countries": [],
                    "ingredients": [],
                    "categories": [category],
                    "references": [
                        {
                            "title": "FAO (1998) — Fermented fruits and vegetables, a global perspective",
                            "ref_type": "literature",
                            "url": FAO_CH2_URL,
                            "doi": None,
                        }
                    ],
                    "source_tag": "fao1998",
                }
            )
    return records


def _load_rows() -> list[dict]:
    if not RAW_PATH.exists():
        resp = httpx.get(FAO_CH2_URL, follow_redirects=True, timeout=60)
        resp.raise_for_status()
        RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
        RAW_PATH.write_bytes(resp.content)
    tree = html.fromstring(RAW_PATH.read_bytes())
    # La Tabla 2.1 es la primera cuyo encabezado es "Name and region".
    target = None
    for table in tree.xpath("//table"):
        header = table.xpath(".//tr[1]//text()")
        if "Name and region" in " ".join(_norm(t) for t in header):
            target = table
            break
    if target is None:
        return []
    rows = []
    for tr in target.xpath(".//tr"):
        rows.append([_norm(td.text_content()) for td in tr.xpath("./td|./th")])
    return parse_table(rows)


def load_source() -> list[dict]:
    return _load_rows()
