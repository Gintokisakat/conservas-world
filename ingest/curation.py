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

_DISCARD_NAME_RE = re.compile(r"\bcod liver oil\b", re.I)

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
    ("Kiselo mleko", ["kislo mleko", "kiselo mleko", "kiselo mlyako"]),
    ("Danablu", ["dana blu", "danablu"]),
    ("Soumbala", ["soumbala", "sumbala"]),
    ("Gherkin", ["gherkin", "gherkins"]),
    ("Kimchi", ["kimchi", "kim chi"]),
    ("Atchara", ["atchara", "achara"]),
    ("Dadih", ["dadih", "dadiah"]),
    ("Yogurt", ["yogurt", "yogur"]),
    ("Achar", ["achar", "achaar"]),
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
]


def _canon_off(name: str) -> str:
    n = _SIZE_TOKENS.sub(" ", name.lower())
    n = re.sub(r"[\s,;()'’]+", " ", n)
    n = re.sub(r"[^a-z0-9]+", " ", n)
    return re.sub(r"\s+", " ", n).strip()


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
        .where(models.Product.source_tag == "openfoodfacts")
    ).scalars().all()

    groups: dict[str, list] = {}
    for p in prods:
        key = _canon_off(p.name)
        if key:
            groups.setdefault(key, []).append(p)

    groups = {k: v for k, v in groups.items() if len(v) > 1}
    merged = 0
    for members in groups.values():
        members.sort(key=_best_key)
        keep, *rest = members
        for dup in rest:
            seen_aliases = {normalize_name(a.name) for a in keep.aliases}
            if normalize_name(dup.name) not in seen_aliases:
                keep.aliases.append(models.ProductAlias(name=dup.name, language=None))
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
    changed = 0
    for p in prods:
        if _DISCARD_NAME_RE.search(p.name):
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
