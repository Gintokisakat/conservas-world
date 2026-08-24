#!/usr/bin/env python
"""Genera los CSV de revisión manual por región (fuentes académicas).

Los CSV resultantes tienen columnas:
    include,name,country,substrate,category,description_es,microbiota,source_ref

Flujo: revisar/marcar include=yes|no|check -> los aprobados se ingieren con
`python -m ingest.sources.review_csv`.
"""

import csv
import re
from pathlib import Path

import httpx
from lxml import html

OUT = Path(__file__).resolve().parent
CACHE = OUT / "_cache"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}


def fetch_cached(url: str, cache_name: str) -> bytes:
    """Descarga con caché local. Si PMC bloquea httpx (challenge), usar:
    curl -sL -A 'Mozilla/5.0' <url> -o review/_cache/<cache_name>"""
    path = CACHE / cache_name
    if path.exists() and path.stat().st_size > 50_000:
        return path.read_bytes()
    resp = httpx.get(url, headers=UA, timeout=60, follow_redirects=True)
    resp.raise_for_status()
    if len(resp.content) < 50_000:
        raise RuntimeError(
            f"{url} devolvió una página de challenge ({len(resp.content)}B). "
            f"Descarga manual: curl -sL -A 'Mozilla/5.0' {url} -o {path}"
        )
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    return resp.content


def _clean(text: str) -> str:
    return " ".join(str(text).split()).strip()


def _cat(substrate: str, name: str = "") -> str:
    blob = f"{substrate} {name}".lower()
    if any(k in blob for k in ("milk", "leche", "yogur", "cheese", "queso", "buttermilk")):
        return "fermento_lactico"
    if any(k in blob for k in ("wine", "vino", "beer", "cerveza", "maize beer", "sorghum beer", "mead", "palm wine", "alcoholic")):
        return "fermento_alcoholico"
    if any(k in blob for k in ("soy", "soja", "locust bean", "castor", "melon seed", "bambara", "sesame")):
        return "fermento_alcalino"
    if any(k in blob for k in ("cassava", "yuca", "tuber", "yam", "potato", "taro", "breadfruit", "banana", "plantain", "maize", "sorghum", "millet", "cereal", "rice", "arroz", "wheat", "trigo", "barley", "cebada", "porridge", "noodle", "bread", "pan ")):
        return "fermento_cereal"  # se ajustará a taxonomy en ingestión
    return "otro"


def _write(filename: str, rows: list[dict]) -> None:
    path = OUT / filename
    fieldnames = ["include", "name", "country", "substrate", "category", "description_es", "microbiota", "source_ref"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row.setdefault("include", "yes")
            for key in fieldnames:
                row.setdefault(key, "")
            writer.writerow(row)
    print(f"{filename}: {len(rows)} filas")


# ---------------------------------------------------------------------------
# África Oriental (PMC11877266) — tablas estructuradas abiertas
# ---------------------------------------------------------------------------

EAST_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11877266/"


def build_africa_east() -> None:
    tree = html.fromstring(fetch_cached(EAST_URL, "pmc_east.html"))
    tables = tree.xpath("//table")
    rows_out = []
    seen = set()
    for ti in (0, 1):
        if ti >= len(tables):
            continue
        for tr in tables[ti].xpath(".//tr")[1:]:
            cells = [_clean(c.text_content()) for c in tr.xpath("./th|./td")]
            if len(cells) < 4 or not cells[1]:
                continue
            substrate, name, country = cells[0], cells[1], cells[2]
            ref = cells[3] if len(cells) > 3 else ""
            # limpiar notas tipo 'a'/'b' al pie
            name = re.sub(r"\s*[ab]\s*$", "", name).strip()
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            rows_out.append(
                {
                    "name": name,
                    "country": country,
                    "substrate": substrate,
                    "category": _cat(substrate, name),
                    "description_es": f"Fermento tradicional del Este de África ({country}); materia prima: {substrate}.",
                    "source_ref": f"Food Sci Nutr. (2025) PMC11877266 — {ref}",
                }
            )
    _write("africa_east.csv", rows_out)


# ---------------------------------------------------------------------------
# África (PMC8857253) — tabla sustrato/alimento/microbiota/origen
# ---------------------------------------------------------------------------

WEST_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8857253/"


def build_africa_west() -> None:
    tree = html.fromstring(fetch_cached(WEST_URL, "pmc_africa.html"))
    tables = tree.xpath("//table")
    rows_out = []
    if not tables:
        _write("africa_west.csv", rows_out)
        return
    for tr in tables[0].xpath(".//tr")[1:]:
        cells = [_clean(c.text_content()) for c in tr.xpath("./th|./td")]
        if len(cells) < 4 or not cells[1]:
            continue
        substrate, foods, micro, origin = cells[0], cells[1], cells[2], cells[3]
        # nombres separados por coma o espacios ambiguos: marcar para revisión si hay ambigüedad
        parts = [p.strip() for p in foods.split(",") if p.strip()]
        ambiguous = len(parts) == 1 and len(foods.split()) > 3
        include = "check" if ambiguous else "yes"
        names = parts if parts else [foods]
        if ambiguous:
            names = [foods]
        for name in names:
            rows_out.append(
                {
                    "include": include,
                    "name": name,
                    "country": origin,
                    "substrate": substrate,
                    "category": _cat(substrate, name),
                    "description_es": f"Fermento africano sobre {substrate}; microbiota láctica documentada.",
                    "microbiota": micro,
                    "source_ref": "Microorganisms (2022) PMC8857253",
                }
            )
    _write("africa_west.csv", rows_out)


# ---------------------------------------------------------------------------
# MENA — lácteos y cereal+lácteo (datos factuales del review Int Dairy J 2023)
# ---------------------------------------------------------------------------

MENA = [
    ("Laban", "Egipto, Irak, Líbano", "leche"),
    ("Leben", "Egipto, Irak, Líbano, Túnez", "leche"),
    ("Labneh", "Levante", "yogur escurrido"),
    ("Laben raib", "Arabia Saudí", "leche"),
    ("Mast", "Irán", "leche"),
    ("Zabady", "Egipto, Sudán", "leche"),
    ("Kishk", "Egipto, Siria, Líbano, Jordania", "trigo + yogur"),
    ("Kushuk", "Irak", "trigo + yogur"),
    ("Kashk", "Irán", "trigo + yogur / suero"),
    ("Tarhana", "Turquía", "trigo + yogur + verduras"),
    ("Trahanas", "Grecia, Chipre", "trigo + leche de oveja/cabra"),
    ("Ayran", "Turquía", "leche (bebida)"),
    ("Jameed", "Jordania", "leche de oveja secada"),
    ("Oggtt", "Arabia Saudí", "leche deshidratada"),
    ("Tulum", "Turquía", "leche (madurado en piel)"),
    ("Kurut", "Turquía, Asia Central", "yogur seco"),
    ("Shanklish", "Siria, Líbano", "queso fresco especiado"),
    ("Lben", "Magreb", "leche (bebida)"),
]


def build_mena() -> None:
    rows = [
        {
            "name": n,
            "country": c,
            "substrate": s,
            "category": "fermento_lactico",
            "description_es": f"Lácteo fermentado tradicional de {c}.",
            "source_ref": "Int Dairy J (2023) MENA fermented dairy review",
        }
        for n, c, s in MENA
    ]
    _write("mena_dairy.csv", rows)


# ---------------------------------------------------------------------------
# Asia Central — productos de la ganadería nómada (reviews Int Dairy J)
# ---------------------------------------------------------------------------

CENTRAL_ASIA = [
    ("Qymyz (koumiss)", "Kazajistán, Kirguistán, Mongolia", "leche de yegua"),
    ("Shubat", "Kazajistán", "leche de camella"),
    ("Chal", "Turkmenistán", "leche de camella"),
    ("Khoormog", "Mongolia", "leche de yegua/vaca"),
    ("Qurt (kurt)", "Kazajistán, Kirguistán", "yogur seco salado"),
    ("Irimshik", "Kazajistán", "leche de oveja/cabra (queso seco)"),
    ("Souzma", "Kazajistán", "yogur escurrido"),
    ("Ayran", "Turquía, Cáucaso, Asia Central", "leche (bebida)"),
    ("Tan", "Armenia, Azerbaiyán", "leche (bebida de yogur)"),
    ("Ryazhenka", "Rusia, Kazajistán", "leche horneada fermentada"),
    ("Prostokvasha", "Rusia", "leche acidificada"),
    ("Kefir", "Cáucaso", "leche con granos de kéfir"),
]


def build_central_asia() -> None:
    rows = [
        {
            "name": n,
            "country": c,
            "substrate": s,
            "category": "fermento_lactico",
            "description_es": f"Lácteo fermentado tradicional de la estepa/cordillera ({c}).",
            "source_ref": "Int Dairy J (2021/2022) Central Asia dairy reviews",
        }
        for n, c, s in CENTRAL_ASIA
    ]
    _write("central_asia.csv", rows)


# ---------------------------------------------------------------------------
# Oceanía — pits de fermentación del Pacífico (literatura etnobotánica)
# ---------------------------------------------------------------------------

OCEANIA = [
    ("Masi (Samoa)", "Samoa", "fruta de pan entera o pelada"),
    ("Ma mei", "Tonga", "fruta de pan"),
    ("Ma kape", "Tonga", "taró Alocasia"),
    ("Ma hopa", "Tonga", "plátano"),
    ("Bwiru", "Islas Marshall", "fruta de pan en pit"),
    ("Davuke", "Fiyi", "fruta de pan/taro/yuca en pit"),
    ("Maa (Marquesas)", "Polinesia Francesa", "fruta de pan"),
    ("Poi 'ulu", "Hawái", "fruta de pan cocida machacada"),
    ("Poi (taro)", "Hawái", "taró Colocasia"),
    ("Kānga pirau", "Nueva Zelanda", "maíz fermentado (maorí)"),
    ("Anuta pit ferment", "Islas Salomón/Anuta", "taró, yuca, plátano"),
]


def build_oceania() -> None:
    rows = [
        {
            "name": n,
            "country": c,
            "substrate": s,
            "category": "encurtido_fermentado",
            "description_es": "Fermentación en fosas tradicional del Pacífico (lacto-fermentación anaerobia).",
            "source_ref": "Pollock (1984) JSO; Atchley & Cox (1985); Aalbersberg (1988)",
        }
        for n, c, s in OCEANIA
    ]
    _write("oceania.csv", rows)


# ---------------------------------------------------------------------------
# Latinoamérica — review Ecuador (MDPI 2022) + clásicos andinos/mesoamericanos
# ---------------------------------------------------------------------------

LATAM = [
    ("Chicha de jora", "Perú, Ecuador, Bolivia", "maíz malteado"),
    ("Chicha de cassava", "Ecuador (Amazonía), Brasil", "yuca mascada"),
    ("Chicha de Yamor", "Ecuador (Otavalo)", "siete maíces"),
    ("Champús", "Ecuador, Colombia", "maíz + frutas + panela"),
    ("Chaguarmishqui", "Ecuador", "savia de agave fermentada"),
    ("Pulque", "México", "aguamiel de maguey"),
    ("Tesgüino", "México (Sierra Tarahumara)", "maíz germinado"),
    ("Guarapo", "Colombia, Venezuela", "panela/jugo de caña"),
    ("Caxiri", "Brasil (Amazonía)", "yuca"),
    ("Cauim", "Brasil (indígena)", "yuca/arroz"),
    ("Chontaduro fermentado", "Ecuador, Colombia", "durazno de palma"),
]


def build_latam() -> None:
    rows = [
        {
            "name": n,
            "country": c,
            "substrate": s,
            "category": "fermento_alcoholico",
            "description_es": "Fermento tradicional prehispánico/colonial latinoamericano.",
            "source_ref": "Foods (2022) 11:1854 Ecuador review; Tamang & Samuel compilations",
        }
        for n, c, s in LATAM
    ]
    _write("latam.csv", rows)


# ---------------------------------------------------------------------------
# México — Atlas/Curso de quesos artesanales (Colegio de Postgraduados)
# ---------------------------------------------------------------------------

MEX_QUESOS = [
    ("Queso Crema de Chiapas", "Chiapas"), ("Queso Bola de Ocosingo", "Chiapas"),
    ("Quesillo de la Costa de Chiapas", "Chiapas"), ("Quesillo del Norte de Chiapas", "Chiapas"),
    ("Queso Poro de Tabasco", "Tabasco"), ("Queso Añejo de Zacatecas", "Zacatecas"),
    ("Queso Menonita (Chihuahua)", "Chihuahua"), ("Queso de la Sierra (Durango)", "Durango"),
    ("Queso Oaxaca de Aculco", "Estado de México"), ("Queso Chapingo", "Estado de México"),
    ("Queso Panela de Chapingo", "Estado de México"), ("Queso Ranchero", "Estado de México"),
    ("Queso Botanero", "Estado de México"), ("Queso Añejo de Zacazonapan", "Estado de México"),
    ("Adobera de Los Altos", "Jalisco"), ("Adobera de la Sierra de Amula", "Jalisco"),
    ("Panela de Soyatlán", "Jalisco"), ("Cotija", "Michoacán/Jalisco"),
    ("Chongos Zamoranos", "Michoacán"), ("Queso Tepeque", "Michoacán"),
    ("Quesillo de Los Reyes Etla", "Oaxaca"), ("Queso de Aro de Etla", "Oaxaca"),
    ("Queso Seco Encerado del Istmo", "Oaxaca"), ("Queso Fresco de Chiautla", "Puebla"),
    ("Queso Seco de Chiautla", "Puebla"), ("Queso de Prensa de la Costa Chica", "Guerrero/Oaxaca"),
    ("Queso Seco de la Tierra Caliente", "Guerrero"), ("Queso Tenate de Hidalgo", "Hidalgo"),
    ("Queso Asadero de Aguascalientes", "Aguascalientes"), ("Queso Fresco de Mazatán", "Sonora"),
    ("Queso Cocido de Sonora", "Sonora"), ("Queso Ahumado de la Joya", "Veracruz"),
    ("Queso Enreatado (de Cincho)", "Veracruz"), ("Queso de Hoja de Veracruz", "Veracruz"),
    ("Queso Jarocho", "Veracruz"), ("Queso Tenate de Tlaxco fresco", "Tlaxcala"),
    ("Queso Tenate de Tlaxco madurado", "Tlaxcala"), ("Queso Guaje de Tanquian", "San Luis Potosí"),
]


def build_mexico() -> None:
    rows = []
    for name, state in MEX_QUESOS:
        rows.append(
            {
                "name": name,
                "country": f"México ({state})",
                "substrate": "leche cruda de vaca (artesanal)",
                "category": "fermento_lactico",
                "description_es": "Queso artesanal mexicano genuino documentado por el Colegio de Postgraduados.",
                "source_ref": "Atlas/Curso Quesos Artesanales Mexicanos, Colegio de Postgraduados",
            }
        )
    _write("mexico_quesos.csv", rows)


if __name__ == "__main__":
    build_africa_east()
    build_africa_west()
    build_mena()
    build_central_asia()
    build_oceania()
    build_latam()
    build_mexico()
    print("CSVs de revisión generados en review/")
