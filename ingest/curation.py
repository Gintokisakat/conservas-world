import argparse
import re
from difflib import SequenceMatcher
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import models
from app.db.database import SessionLocal
from ingest.normalize import normalize_name

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_SIZE_TOKENS = re.compile(
    r"\b\d+[,.]?\d*\s*(g|gr|kg|ml|l|cl|dl|oz|lb|grs|gramos|litros?|kilos?)\b|"
    r"\b\d+\b|"
    r"\b(bo[îi]te de|pack de|paquet de|bote de|brik de|brik)\b",
    re.I,
)

_DISCARD_NAME_RE = re.compile(
    r"\bcod liver oil\b"
    r"|^list of\b"
    r"|^lists of\b"
    r"|\b(food brand|pickle brand|drink brand|beverage brand|brand of)\b"
    r"|\b(empresa|compan[yí]a|company)\b"
    r"|preparation and preservation of"
    r"|aggregation of particles",
    re.I,
)

# Marcadores de ruido que solo aparecen en la descripción/metodo (no en el nombre).
_DISCARD_TEXT_RE = re.compile(
    r"\b(food brand|pickle brand|drink brand|beverage brand)\b"
    r"|\bempresa\b"
    r"|preparation and preservation of"
    r"|aggregation of particles",
    re.I,
)

# Productos de marca/ruido (sin ingredientes ni descripción) que se descartan.
CURATED_DISCARDS = [
    # Entradas rotas de "List of cheeses" (descripción = "nan") y lugares/personas.
    "Condiment",
    "Qudam",
    "Abaza",
    "Arnavut",
    "Edirne",
    "Sayas",
    "Enredo",
    "Lingallin",
    "Criollo",
    "Goya",
    "Chubut",
    "Tandil",
    "Mar del Plata",
    "Tafí del Valle",
    # Nombres de marca sueltos de OpenFoodFacts (sin ingredientes ni descripción).
    "Corbeille Louise",
    "Delicius Sicilia",
    "Delicius Cantabrico",
    "Delicius",
    "Reserva",
    "Delicious Aperitivo",
    "Parma",
    "Oceanos",
]


# Grupos curados: mismo producto con grafías/lenguas distintas (canónico, variantes).
# Las variantes se comparan con normalize_name (sin acentos/espacios).
CURATED_MERGES = [
    ("Vinaigre de cidre de pomme", ["vinaigre de cidre de pomme", "vinaigre de cidre de pommes"]),
    ("Vinaigre de cidre", ["vinaigre de cidre", "le vinaigre de cidre", "vinaigre de cidre 5 d acidite"]),
    ("Vinaigre d'alcool coloré", ["vinaigre alcool colore", "vinaigre d alcool colore"]),
    ("Vinaigre balsamique de Modena", [
        "vinaigre balsamique de modena",
        "vinaigre balsamique de modene",
        "vinaigre basalmique de modene",
    ]),
    ("Crème au vinaigre balsamique de Modène", [
        "crème avec vinaigre balsamique de molène",
        "crème au vinaigre balsamique de modene",
    ]),
    ("Pickled onions", ["pickled onion", "pickled onions"]),
    ("Myeolchijeot", ["myeolchi jeot", "myeolchijeot"]),
    ("Sukakomasu", ["sukakomasu", "suka ko masu"]),
    ("Aceitunas verdes deshuesadas", ["aceitunas verdes deshuesadas"]),
    ("Pepinillos", ["pepinillos"]),
    ("Vinagre de manzana", ["vinagre de manzana"]),
    ("Salsa soja", ["salsa soja"]),
    ("Filetes de Anchoa", ["Filetes de anchoa"]),
    ("Kiselo mleko", ["kislo mleko", "kiselo mleko", "kiselo mlyako"]),
    ("Danablu", ["dana blu", "danablu"]),
    ("Soumbala", ["soumbala", "sumbala"]),
    ("Gherkin", ["gherkin", "gherkins"]),
    ("Kimchi", ["kimchi", "kim chi"]),
    ("Atchara", ["atchara", "achara"]),
    ("Dadih", ["dadih", "dadiah"]),
    ("Yogurt", ["yogurt", "yogur"]),
    ("Achar", ["achar", "achaar", "achiar"]),
    ("Fish sauce", ["fish sauce", "fischsauce", "fish souce"]),
    ("Kvass", ["kvass", "kvas"]),
    ("Miso", ["miso", "misso"]),
    ("Kashkaval", ["kashkaval", "kashkawal", "kashkawan"]),
    ("Ayibe", ["ayib", "ayibe"]),
    ("Bekasang", ["bakasang", "bekasang"]),
    ("Halloumi", ["halloumi", "halumi"]),
    ("Herring", ["hirring", "herring"]),
    ("Smetana", ["smetana", "smotana"]),
    ("Tarhana", ["tarhana", "trahana"]),
    ("Avakaya", ["aavakaaya", "avakaya"]),
    ("Tempeh", ["tempeh", "tempe"]),
    ("Weinsauerkraut", ["wein sauerkraut", "weinsauerkraut"]),
    ("Miso paste", ["miso paste", "misopaste"]),
    ("Miso Paste dunkel", ["misopaste dunkel", "miso paste dunkel"]),
    ("Sojasauce", ["sojasauce", "soja sauce"]),
    ("Soja Sauce Shoyu", ["soja sauce shoyu", "sojasouce shoyu"]),
    ("Pepinillo", ["pepinillos", "pepinillo"]),
    ("Rote Beete", ["rote beete", "rote bete"]),
    ("Rote Beete in Scheiben", ["rote beete in scheiben", "rote beete scheiben"]),
    ("Tempeh natural", [
        "bio tempeh nature",
        "bio tempeh natural",
        "bio tempeh natur",
        "tempeh natur",
        "tempeh nature",
        "tempeh naturale",
        "tempeh al naturale",
    ]),
    ("Tempeh de soja", ["tempeh de soja", "tempeh soja", "tempe de soja"]),
    ("Smoked tempeh", ["smoked tempeh", "smoky tempeh"]),
    ("Tempeh original", ["tempeh l originale", "tempeh original"]),
    ("Kefir yoghurt", ["kefir yogurt", "kefir yoghurt"]),
    ("Essiggurken", ["essiggurken", "esiggurken"]),
    ("Choucroute d'Alsace", ["choucroute alsace", "choucroute d alsace"]),
    ("Choucroute cuisinée", ["choucroute cuisinée", "la choucroute cuisinée"]),
    ("Choucroute au vin blanc", ["choucroute garnie au vin blanc", "choucroute cuite au vin blanc"]),
    ("Choucroute cuisinée au riesling", [
        "choucroute cuisinée au riesling",
        "choucroute cuite au riesling",
    ]),
    ("Cornichons aigres-doux", [
        "cornichon aigre doux",
        "cornichons aigre doux",
        "cornichons aigres doux",
    ]),
    ("Cornichons extra-fins", ["cornichons extra fins", "cornichons extra fin"]),
    ("Pepinillos en vinagre", ["pepinillos en vinagre", "pepinillos vinagre"]),
    ("Sauce nuoc mam à la citronnelle", [
        "sauce nuoc mam a la citronnelle",
        "sauce nuoc mam a la citronelle",
    ]),
    ("Sauce nuoc mam", ["sauce nuoc mam", "sauc nuoc mam"]),
    ("Sauce soja sucrée", ["sauce soja sucrée", "sauce de soja sucrée"]),
    ("Sauce de soja aux champignons", [
        "sauce de soja aux champignons",
        "sauce soja aux champignons",
    ]),
    ("Sauce soja allégée en sel", [
        "sauce soja allégée en sel",
        "sauce shoyu allégé en sel",
    ]),
    ("Sauce de poisson", ["sauce de poisson", "sauce poisson"]),
    ("Salsa de soja", ["salsa de soja", "salsa soja"]),
    ("Vinagre de manzana", ["vinagre de manzana", "vinagre manzana"]),
    ("Vegan kimchi", ["vegan kimchi", "vegansk kimchi"]),
    ("Kéfir nature", ["kéfir nature", "kéfir natural", "kefir naturel"]),
    ("Pâte miso", ["pâta miso", "pâte miso", "pâte de miso"]),
    ("Miso blanc", ["miso blanc", "miso bianco"]),
    ("Kombucha framboise", ["kombucha framboise", "kombucha framboesa"]),
    ("Organic kombucha ginger lemon", [
        "organic kombucha ginger lemonade",
        "organic kombucha ginger lemon",
    ]),
    ("Confiture de fraises allégée en sucres", [
        "Confiture de Fraise Allégée en sucres",
        "Confiture fraises allégée en sucres",
    ]),
    ("Confiture allégée framboise", ["Confiture allégée Framboises"]),
    ("Filets de hareng fumés doux", ["Filets de hareng fumé doux"]),
    ("Filets de harengs fumés", ["Filets de hareng fumes"]),
    ("Truite des Pyrénées fumée", ["Truite des Pyrénées fumées"]),
    ("Confiture Extra Abricot", ["Confiture Extra Abricots"]),
    ("Confiture abricot", [
        "Confiture Abricots",
        "Confiture d'abricot",
        "Confiture d'abricots",
    ]),
    ("Confiture de myrtilles", ["Confiture de myrtille", "Confiture myrtilles"]),
    ("Thon entier au nature", ["Thon entier au naturel", "Thon entier nature"]),
    ("Olives noirs de Nyons", ["Olives noir de nyons"]),
    ("Vinaigre balsamique de Modène boilogique", [
        "Vinaigre balsamique de Modène biologique",
    ]),
    ("Confiture de fraise", [
        "Confiture de fraises",
        "Confiture Fraises",
        "Confiture fraise",
    ]),
    ("Confiture Framboises", ["Confiture Framboise"]),
    ("Confiture de figue", ["Confiture de figues", "Confiture figues"]),
    ("Filet De Sardines", ["Filets de Sardines", "Filet de sardine"]),
    ("Viande des GRISONS", ["Viande de Grisons"]),
    ("Non-Pareil Capers", ["Nonpareil Capers", "Nonpareille capers"]),
    ("Marmelade orange", ["Marmelade Oranges", "Marmelade d'orange"]),
    ("Rilettes de thon", ["Rillettes De Thon", "Rillettes thon"]),
    ("Bigarreaux confits de provence", ["Bigarreaux Confits en Provence"]),
    ("Écorces d'oranges confites🍊", ["Écorces d'Orange Confites"]),
    ("Saumon fumé Le Norvège", ["Saumon fumé de Norvège", "Saumon fumé norvège"]),
    ("Abricot 65% de fruit", ["Abricot, 65% de fruits"]),
    ("Olives noires confites", ["Olives noir confites"]),
    ("Bresaola della valtellina i.g.p.", ["Bresaola della valtellina IGP"]),
    ("Filets de Sardine (au Naturel)", ["Filets de sardines au naturel"]),
    ("Le thon blanc au naturel germon", ["Thon blanc au naturel Germon"]),
    ("Choucroute garnie d'Alsace VPF VBF 700g", [
        "Choucrout garnie d'Alsace VPF VBF 1400g",
    ]),
    ("Olives noires entières à la grecque", [
        "Olives Noires Entieres à la a Grecque",
    ]),
    ("Olives noires à la grecques denoyautees", [
        "Olives noires à la grecque dénoyautées",
    ]),
    ("Sardines", ["Sardine"]),
    ("Citrons Confits", ["Citron confit"]),
    ("Marmelade - Fruchtaufstrich Erdbeere", [
        "Marmelade/Fruchtaufstrich Erdbeeren",
    ]),
    ("Sardines à l'huile d'olive vierge extra bio", [
        "Sardines, huile d'olive vierge extra bio",
    ]),
    ("Truite fumée, Aquitaine", ["Truite fumée d'Aquitaine"]),
    ("Atún con tomate", ["Atún en tomate"]),
    ("Confiture d'Orange", ["Confiture à l'orange"]),
    ("Saumon fumé d'Ecosse", ["Saumon Fumé Écosse"]),
    ("MACEDOINE DE FRUITS CONFITS", ["Macédoine fruits confits"]),
    ("Awase Miso", ["Aware miso"]),
    ("Filetti acciughe sott'olio", ["Filetto do acciughe sott'olio"]),
    ("Frutti di cappero", ["Frutti di capperi", "Frutto del cappero"]),
    ("Danino", ["Danonino"]),
    ("Liliput", ["Liliputas"]),
    ("Ikivunde", ["Kivunde"]),
    ("Kefír Or Acidofilní Mléko", ["Kefír Or Acidofilné Mlieko"]),
    ("Confiture Extra Fraise", ["Confiture extra de Fraises"]),
    ("Thon à l'huile végétale", ["Thon a huile végétale"]),
    ("DOLCE À base d'\"Aceto Balsamico di Modena IGP\"", [
        "Douceur à base d'\"Aceto Balsamico di Modena IGP\"",
    ]),
    ("Filetti di alice", ["Filetti di Alici"]),
    ("Choucroute garnie alsacienne , 390g", [
        "Choucroute garnie d'Alsace , 970g",
    ]),
    ("Caper", ["Capers"]),
]


def _canon_off(name: str) -> str:
    n = _SIZE_TOKENS.sub(" ", name.lower())
    n = re.sub(r"[\s,;()'’]+", " ", n)
    n = re.sub(r"[^a-z0-9]+", " ", n)
    return re.sub(r"\s+", " ", n).strip()


# Palabras función que se ignoran al comparar nombres dentro de un grupo curado.
_STOP_TOKENS = frozenset({
    "de", "d", "a", "l", "la", "le", "les", "au", "aux", "en", "des", "du",
    "un", "une", "el", "los", "las", "del", "di", "della", "delle", "dei",
    "con", "the", "of", "and", "or", "to", "at", "in", "with", "from", "for",
    "on", "por", "para", "et", "und", "van", "von",
})

# Correcciones de grafía (typos/plurales no regulares) aplicadas al comparar contenido.
_TOKEN_FIXES = {
    "rilettes": "rillettes",
    "boilogique": "biologique",
    "aware": "awase",
    "naturel": "nature",
    "erdbeeren": "erdbeere",
    "liliputas": "liliput",
    "achiar": "achar",
    "danonino": "danino",
    "ikivunde": "kivunde",
    "dolce": "douceur",
    "alice": "alici",
    "alsacienne": "alsace",
}


def _content_tokens(name: str) -> list[str]:
    toks = []
    for t in normalize_name(name).split():
        if len(t) == 1 or t in _STOP_TOKENS:
            continue
        t = _TOKEN_FIXES.get(t, t)
        if len(t) >= 5 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        toks.append(t)
    return toks


def _content_key(name: str) -> frozenset[str]:
    return frozenset(_content_tokens(name))


def _title_case(name: str) -> str:
    if any(c.isupper() for c in name):
        return name
    if name.isupper():
        return name
    if re.fullmatch(r"[\w .\-'/()´`’]+", name, re.UNICODE) is None:
        return name
    return name.title()


def _best_key(p):
    return (-len(p.description or ""), -len(p.ingredients), -len(p.name))


def _absorb_into(keep, dup, seen_aliases):
    if normalize_name(dup.name) not in seen_aliases:
        keep.aliases.append(models.ProductAlias(name=dup.name, language=None))
        seen_aliases.add(normalize_name(dup.name))
    for alias in dup.aliases:
        if normalize_name(alias.name) not in seen_aliases:
            keep.aliases.append(models.ProductAlias(name=alias.name, language=alias.language))
            seen_aliases.add(normalize_name(alias.name))
    for ref in dup.references:
        if ref not in keep.references:
            keep.references.append(ref)
    for item in dup.ingredients:
        if item not in keep.ingredients:
            keep.ingredients.append(item)
    for item in dup.countries:
        if item not in keep.countries:
            keep.countries.append(item)
    for item in dup.categories:
        if item not in keep.categories:
            keep.categories.append(item)
    for item in dup.microbes:
        if item not in keep.microbes:
            keep.microbes.append(item)
    dup.status = "discarded"


def merge_curated(session) -> tuple[int, int]:
    """Fusiona los grupos de CURATED_MERGES: variantes con grafías/lenguas
    distintas del mismo producto (nombre exacto normalizado o contenido
    equivalente: mismas palabras tras quitar artículos/plurales/typos)."""
    prods = session.execute(
        select(models.Product)
        .options(
            selectinload(models.Product.aliases),
            selectinload(models.Product.references),
            selectinload(models.Product.ingredients),
            selectinload(models.Product.countries),
            selectinload(models.Product.categories),
            selectinload(models.Product.microbes),
        )
        .where(models.Product.status != "discarded")
    ).scalars().all()

    by_name: dict[str, list] = {}
    by_content: dict[frozenset[str], list] = {}
    for p in prods:
        by_name.setdefault(normalize_name(p.name), []).append(p)
        by_content.setdefault(_content_key(p.name), []).append(p)

    groups = 0
    merged = 0
    for canonical, variants in CURATED_MERGES:
        candidates = {}
        for variant in [canonical, *variants]:
            for p in by_name.get(normalize_name(variant), []):
                candidates[p.id] = p
            for p in by_content.get(_content_key(variant), []):
                candidates[p.id] = p
        active = [p for p in candidates.values() if p.status != "discarded"]
        if len(active) < 2:
            continue
        active.sort(key=_best_key)
        keep, *rest = active
        seen_aliases = {normalize_name(keep.name)} | {
            normalize_name(a.name) for a in keep.aliases
        }
        for dup in rest:
            _absorb_into(keep, dup, seen_aliases)
            merged += 1
        groups += 1
    return groups, merged


def merge_off_variants(session) -> tuple[int, int]:
    prods = session.execute(
        select(models.Product)
        .options(
            selectinload(models.Product.aliases),
            selectinload(models.Product.references),
            selectinload(models.Product.ingredients),
            selectinload(models.Product.countries),
            selectinload(models.Product.categories),
            selectinload(models.Product.microbes),
        )
        .where(
            models.Product.source_tag == "openfoodfacts",
            models.Product.status != "discarded",
        )
    ).scalars().all()

    groups: dict[str, list] = {}
    for p in prods:
        key = _canon_off(p.name)
        if key and len(key) >= 8:
            groups.setdefault(key, []).append(p)

    groups = {k: v for k, v in groups.items() if len(v) > 1}
    merged = 0
    for members in groups.values():
        members.sort(key=_best_key)
        keep, *rest = members
        seen_aliases = {normalize_name(keep.name)} | {
            normalize_name(a.name) for a in keep.aliases
        }
        for dup in rest:
            _absorb_into(keep, dup, seen_aliases)
            merged += 1
    return len(groups), merged


def title_case_names(session) -> int:
    prods = session.execute(
        select(models.Product).where(models.Product.status != "discarded")
    ).scalars().all()
    changed = 0
    for p in prods:
        if any(c.isupper() for c in p.name) or p.name.isupper():
            continue
        fixed = _title_case(p.name)
        if fixed and fixed != p.name:
            p.name = fixed
            changed += 1
    return changed


def discard_noise(session) -> int:
    prods = session.execute(
        select(models.Product).where(models.Product.status != "discarded")
    ).scalars().all()
    curated_discards = {normalize_name(n) for n in CURATED_DISCARDS}
    changed = 0
    for p in prods:
        if _DISCARD_NAME_RE.search(p.name):
            p.status = "discarded"
            changed += 1
            continue
        if _DISCARD_TEXT_RE.search(" ".join(filter(None, [p.description, p.method]))):
            p.status = "discarded"
            changed += 1
            continue
        if normalize_name(p.name) in curated_discards:
            p.status = "discarded"
            changed += 1
    return changed


def review_report(session) -> list[tuple[models.Product, models.Product, float]]:
    prods = session.execute(
        select(models.Product).where(models.Product.status != "discarded")
    ).scalars().all()
    pairs = []
    for i in range(len(prods)):
        for j in range(i + 1, len(prods)):
            a, b = prods[i], prods[j]
            if abs(len(a.name) - len(b.name)) > 3:
                continue
            ratio = SequenceMatcher(None, a.name.lower(), b.name.lower()).ratio()
            if ratio > 0.85:
                pairs.append((a, b, ratio))
    pairs.sort(key=lambda t: -t[2])
    return pairs


def run_report():
    session = SessionLocal()
    try:
        pairs = review_report(session)
        lines = [
            "Pares con nombres muy similares (>0.85) que NO se fusionan automáticamente:",
            "",
        ]
        for a, b, ratio in pairs:
            lines.append(f"  [{ratio:.2f}] {a.name!r} <-> {b.name!r} ({a.source_tag}/{b.source_tag})")
        out = DATA_DIR / "curation_review.txt"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Reporte de revisión ({len(pairs)} pares) -> {out}")
    finally:
        session.close()


def run_apply():
    from ingest import loader

    session = SessionLocal()
    try:
        groups, merged = merge_curated(session)
        print(f"Grupos curados fusionados: {merged} productos descartados en {groups} grupos")
        groups, merged = merge_off_variants(session)
        print(f"Variantes OFF fusionadas: {merged} productos descartados en {groups} grupos")
        renamed = title_case_names(session)
        print(f"Nombres capitalizados: {renamed}")
        discarded = discard_noise(session)
        print(f"Ruido descartado: {discarded}")
        session.commit()
        loader.create_full_text_table()
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Curaduría de la base de datos")
    parser.add_argument("--report", action="store_true", help="Genera el reporte de revisión")
    parser.add_argument("--apply", action="store_true", help="Aplica las limpiezas automáticas")
    args = parser.parse_args()
    if args.report:
        run_report()
    if args.apply:
        run_apply()


if __name__ == "__main__":
    main()
