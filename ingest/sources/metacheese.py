"""Fuente MetaCheeseDB (metadata-curated cheese metagenomes) — roadmap 2.13.

MetaCheeseDB (magliulo.github.io/metacheesedb) recopila 1.593 metagenomas de
queso distribuidos en 156 subtipos y 19 países. Los datos se sirven como un
widget HTML (reactable de R) con la tabla completa embebida como JSON en un
bloque <script type="application/json">.

Cada fila es una muestra con abundancia relativa (%) de ~1.200 taxones. Para
cada subtipo calculamos los taxones *característicos* (prevalencia >= 50 % y
abundancia media >= 1 %) y los vinculamos a nuestros productos de queso mediante
matching exacto por nombre normalizado o alias curado (familias como Grana,
Pecorino, Mozzarella di bufala, quesos azules, etc.).
"""

import json
import re
from pathlib import Path

from ingest.normalize import normalize_name

HTML_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "metacheese" / "MetaCheeseDB.html"
)
SOURCE_URL = "https://magliulo.github.io/raffaelemagliulo/files/MetaCheeseDB.html"
PAGE_URL = "https://magliulo.github.io/metacheesedb/"

# Columnas de metadatos de la tabla (no abundancias).
_META_COLUMNS = {
    "SampleID", "Dataset", "Accession", "Run", "Experiment", "Study", "Project",
    "Database", "Macrocategory", "Category", "Type", "Subtype", "Thermisation",
    "Pasteurization", "Skimming", "Backslopping", "Country", "Region",
    "source_database", "accession_number", "title", "link", "samples",
}

# Columnas numéricas de metadatos que no son taxones (caracterización del queso).
_NUMERIC_META = {
    "Subtype_sum", "Year_of_registration", "Temperature_of_curd_processing_Celsius_degree",
    "Ripening_period", "Ripening_temperature_Celsius_degree", "Ripening_relative_humidity",
    "Fat_content_percentage", "Moisture_content",
}

# Umbrales para definir un taxón característico por subtipo.
PREVALENCE_THRESHOLD = 0.50
MEAN_ABUNDANCE_THRESHOLD = 1.0
MAX_TAXA = 10

# Alias curados: subtipo de MetaCheeseDB -> palabras clave en nombre de producto.
# Solo para familias que no casan por nombre exacto y donde la equivalencia es sólida.
# El matching usa límites de palabra para evitar falsos positivos (gouda != goudale).
_CURATED_ALIASES = {
    "Grana": ["grana"],
    "Pecorino": ["pecorino"],
    "Water_buffalo_mozzarella": ["mozzarella di bufala", "mozzarella de bufala"],
    "Blue_cheese": ["blue", "azul", "gorgonzola", "roquefort", "danablu", "stilton"],
    "Noord_Hollandse_Gouda": ["gouda"],
    "Dutch_type_cheese": ["gouda", "edam", "maasdam"],
    "Tomme": ["tomme"],
    "Toma": ["toma"],
    "Caciotta": ["caciotta"],
    "Caciocavallo": ["cacio cavallo", "caciocavallo"],
    "Provolone": ["provolone"],
    "Parmigiano_Reggiano": ["parmigiano", "parmesano", "parmesan"],
    "Feta": ["feta"],
    "Roquefort": ["roquefort"],
    "Queso_Manchego": ["manchego"],
    "Raclette": ["raclette"],
    "Emmental_francais_est_central_PGI": ["emmental", "emental"],
    "Brie": ["brie"],
    "Camembert": ["camembert"],
    "Cheddar": ["cheddar"],
    "Mature_coloured_cheddar": ["cheddar"],
    "Extra_mature_cheddar_white": ["cheddar"],
    "Havarti_PGI": ["havarti"],
    "Stilton": ["stilton"],
    "White_Stilton_Apricot": ["stilton"],
    "Cotija": ["cotija"],
    "Queso_Cotija": ["cotija"],
    "Asiago": ["asiago"],
    "Montasio": ["montasio"],
    "Taleggio": ["taleggio"],
    "Fontina": ["fontina"],
    "Edam": ["edam"],
    "Maasdam": ["maasdam"],
    "Cream_cheese": ["cream cheese", "queso crema", "queso cream"],
    "Neufchatel": ["neufchatel", "neufchâtel"],
    "Fontal": ["fontal"],
    "Scamorza": ["scamorza"],
    "Provola": ["provola"],
    "Primo_sale": ["primo sale"],
    "Bitto": ["bitto"],
    "Los_beyos": ["los beyos"],
    "Gamoneu": ["gamoneu"],
    "Wagashi": ["wagashi"],
    "Jibneh": ["jibneh", "jibna"],
    "Mahon": ["mahón", "mahon"],
    "Puzzone": ["puzzone"],
    "Tarentaise": ["tarentaise"],
    "Bethlehem": ["bethlehem"],
    "Milleens": ["milleens"],
    "Stichelton": ["stichelton"],
    "Stawley": ["stawley"],
    "Rush_creek_reserve": ["rush creek"],
    "Gersters_Rosmarinkase": ["rosmarinkase"],
    "Heumilch_Bergkaese": ["heumilch", "bergkaese"],
    "Vorarlberger_Bergkase": ["vorarlberger"],
    "Tibet_Traditional_cheese": ["tibet"],
    "Inner_Mongolia_Traditional_cheese": ["inner mongolia"],
}

_CURATED_ALIAS_RES = {
    subtype: [re.compile(rf"\b{re.escape(kw)}\b", re.I) for kw in kws]
    for subtype, kws in _CURATED_ALIASES.items()
}


def _ensure_html():
    if HTML_PATH.exists():
        return
    import httpx

    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    resp = httpx.get(SOURCE_URL, follow_redirects=True, timeout=120)
    resp.raise_for_status()
    HTML_PATH.write_bytes(resp.content)


def _load_table() -> dict[str, list]:
    """Devuelve el dict columna -> lista de valores de la tabla embebida."""
    _ensure_html()
    text = HTML_PATH.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        r'<script type="application/json" data-for="htmlwidget-[^"]+">(.*?)</script>',
        text,
        re.S,
    )
    if not match:
        raise RuntimeError("No se encontró el bloque JSON de datos en el HTML de MetaCheeseDB")
    payload = json.loads(match.group(1))
    return payload["x"]["tag"]["attribs"]["data"]


def _num(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return 0.0


def _taxa_columns(columns: list[str]) -> list[str]:
    return [c for c in columns if c not in _META_COLUMNS and c not in _NUMERIC_META]


def _subtype_taxa(table: dict[str, list]) -> dict[str, dict]:
    """Por subtipo: {taxon: {"mean": float, "prevalence": float}} (solo característicos)."""
    subtypes = table["Subtype"]
    taxa = _taxa_columns(list(table.keys()))
    n_samples = len(subtypes)
    out: dict[str, dict] = {}
    for i in range(n_samples):
        subtype = subtypes[i]
        bucket = out.setdefault(subtype, {})
        for taxon in taxa:
            val = _num(table[taxon][i])
            if val <= 0:
                continue
            stats = bucket.get(taxon)
            if stats is None:
                bucket[taxon] = {"sum": val, "count": 1}
            else:
                stats["sum"] += val
                stats["count"] += 1
    result: dict[str, dict] = {}
    for subtype, bucket in out.items():
        total = sum(1 for s in subtypes if s == subtype) or 1
        kept = {}
        for taxon, stats in bucket.items():
            mean = stats["sum"] / total
            prevalence = stats["count"] / total
            if prevalence >= PREVALENCE_THRESHOLD and mean >= MEAN_ABUNDANCE_THRESHOLD:
                kept[taxon] = {"mean": round(mean, 2), "prevalence": round(prevalence, 3)}
        result[subtype] = kept
    return result


def _microbe_name(taxon: str) -> str:
    return taxon.replace("_", " ").strip()


def _taxa_sorted(subtype: str, subtype_taxa: dict[str, dict]) -> list[dict]:
    """Top MAX_TAXA taxones por abundancia media (formato para taxa_json)."""
    taxa = subtype_taxa[subtype]
    ordered = sorted(taxa.items(), key=lambda kv: -kv[1]["mean"])
    return [
        {
            "name": _microbe_name(taxon),
            "mean_abundance": stats["mean"],
            "prevalence": stats["prevalence"],
        }
        for taxon, stats in ordered[:MAX_TAXA]
    ]


def _sample_count(table: dict[str, list], subtype: str) -> int:
    return sum(1 for s in table["Subtype"] if s == subtype)


def _subtypes_with_taxa() -> dict[str, dict]:
    table = _load_table()
    subtype_taxa = _subtype_taxa(table)
    out = {}
    for subtype in sorted(subtype_taxa):
        out[subtype] = {
            "subtype": subtype,
            "sample_count": _sample_count(table, subtype),
            "taxa": _taxa_sorted(subtype, subtype_taxa),
        }
    return out


def load_source() -> list[dict]:
    """MetaCheeseDB no aporta productos nuevos; solo enriquece los existentes."""
    return []


def _is_dairy(product) -> bool:
    return any(c.code == "fermento_lactico" for c in product.categories)


def _match_subtype_to_products(subtype: str, products: list) -> list:
    """Devuelve los productos que corresponden a un subtipo (exacto o alias curado).

    El match exacto por nombre normalizado tiene prioridad. El alias curado solo
    se aplica cuando no hay match exacto y exige que el producto sea lácteo, para
    evitar falsos positivos (gouda != goudale, blue != blueberry)."""
    key = normalize_name(subtype)
    exact = []
    alias = []
    for product in products:
        name = product.name
        if normalize_name(name) == key:
            exact.append(product)
            continue
        patterns = _CURATED_ALIAS_RES.get(subtype)
        if not patterns:
            continue
        if any(p.search(name) for p in patterns) and _is_dairy(product):
            alias.append(product)
    return exact or alias


def populate_metacheese(session) -> int:
    """Vincula metagenomas MetaCheeseDB a productos por subtipo (tabla
    cheese_metagenomes). Devuelve el número de productos enriquecidos.

    La tabla es 1:1 con products, así que cuando un producto coincide con varios
    subtipos (p. ej. Cheddar y Extra_mature_cheddar_white) gana el match exacto;
    entre alias de igual calidad gana el subtipo alfabéticamente menor."""
    from app.db import models
    from sqlalchemy import select

    subtype_data = _subtypes_with_taxa()
    products = session.execute(select(models.Product)).scalars().all()

    dairy_ids = {
        pid
        for pid, in session.execute(
            select(models.product_category.c.product_id)
            .join(models.Category, models.Category.id == models.product_category.c.category_id)
            .where(models.Category.code == "fermento_lactico")
        )
    }
    name_key = {normalize_name(p.name): p for p in products}

    best: dict[int, tuple[int, str]] = {}
    for subtype, info in subtype_data.items():
        if not info["taxa"]:
            continue
        patterns = _CURATED_ALIAS_RES.get(subtype)
        exact_product = name_key.get(normalize_name(subtype))
        for product in products:
            quality = -1
            if exact_product is product:
                quality = 1
            elif patterns and any(
                p.search(product.name) for p in patterns
            ) and product.id in dairy_ids:
                quality = 0
            if quality < 0:
                continue
            prev = best.get(product.id)
            if prev is None or quality > prev[0] or (quality == prev[0] and subtype < prev[1]):
                best[product.id] = (quality, subtype)

    updated = 0
    for product_id, (_, subtype) in best.items():
        info = subtype_data[subtype]
        payload = {
            "subtype": subtype,
            "sample_count": info["sample_count"],
            "taxa_json": json.dumps(info["taxa"], ensure_ascii=False),
            "url": PAGE_URL,
        }
        existing = session.execute(
            select(models.CheeseMetagenome).where(
                models.CheeseMetagenome.product_id == product_id
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(models.CheeseMetagenome(product_id=product_id, **payload))
            updated += 1
        else:
            changed = any(getattr(existing, k) != v for k, v in payload.items())
            if changed:
                for k, v in payload.items():
                    setattr(existing, k, v)
                updated += 1
    session.commit()
    return updated
