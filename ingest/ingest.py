import argparse
import sys

from app.db.database import SessionLocal, init_db

from ingest.normalize import normalize_name

# Open Food Facts quedó excluida por calidad: traía SKUs comerciales de
# supermercado (ultraprocesados, conservas industriales sin valor
# tradicional). Ver README "Curaduría". El módulo sigue disponible para
# ingesta manual con --sources openfoodfacts.
SOURCES = ["fermdb", "wikipedia", "wikidata", "wikidata_deep", "regional", "fdfdb", "metacheese", "eambrosia", "fao1998"]


def run(sources: list[str], reset: bool = False):
    from app.db import models  # noqa: F401

    from ingest import loader

    if reset:
        import os

        from app.db.database import engine

        if os.path.exists(engine.url.database):
            engine.dispose()
            os.remove(engine.url.database)

    init_db()

    session = SessionLocal()
    try:
        loader.seed_categories(session)
        from ingest.sources.glossary import seed_glossary

        seed_glossary(session)
        seen = set()
        total = 0
        skipped = 0
        by_source = {}
        for source in sources:
            if source == "fermdb":
                from ingest.sources import fermdb
            elif source == "wikipedia":
                from ingest.sources import wikipedia
            elif source == "openfoodfacts":
                from ingest.sources import openfoodfacts
            elif source == "wikidata":
                from ingest.sources import wikidata
            elif source == "regional":
                from ingest.sources import regional
            elif source == "fdfdb":
                from ingest.sources import fdfdb
            elif source == "metacheese":
                from ingest.sources import metacheese
            elif source == "eambrosia":
                from ingest.sources import eambrosia
            elif source == "wikidata_deep":
                from ingest.sources import wikidata_deep
            elif source == "fao1998":
                from ingest.sources import fao1998
            else:
                raise ValueError(f"Fuente desconocida: {source}")
            print(f"Ingiriendo fuente: {source} ...", flush=True)
            try:
                if source == "fermdb":
                    records = fermdb.load_source()
                elif source == "wikipedia":
                    records = wikipedia.load_source()
                elif source == "openfoodfacts":
                    records = openfoodfacts.load_source()
                elif source == "wikidata":
                    records = wikidata.load_source()
                elif source == "fdfdb":
                    records = fdfdb.load_source()
                elif source == "metacheese":
                    records = metacheese.load_source()
                elif source == "eambrosia":
                    records = eambrosia.load_source()
                elif source == "wikidata_deep":
                    records = wikidata_deep.load_source()
                elif source == "fao1998":
                    records = fao1998.load_source()
                else:
                    records = regional.load_source()
            except Exception as exc:
                # Una fuente caída (rate-limit, 5xx, red) no debe tumbar el
                # build completo: se registra y se continúa con el resto.
                print(f"[{source}] FUENTE FALLIDA: {exc}", flush=True)
                by_source[source] = 0
                continue
            by_source[source] = len(records)
            for record in records:
                key = normalize_name(record["name"])
                if key in seen:
                    skipped += 1
                    continue
                seen.add(key)
                product = loader.upsert_product(session, record)
                if product is not None:
                    total += 1
        session.commit()
        if "fdfdb" in sources:
            from ingest.sources import fdfdb

            dairy = fdfdb.populate_dairy(session)
            print(f"Metadatos de lácteos FDF-DB vinculados: {dairy}", flush=True)
        if "metacheese" in sources:
            from ingest.sources import metacheese

            metagenomes = metacheese.populate_metacheese(session)
            print(f"Metagenomas MetaCheeseDB vinculados: {metagenomes}", flush=True)
        added, updated = loader.enrich_ingredients(session)
        uses = loader.build_product_uses(session)
        loader.seed_country_coords(session)
        loader.create_full_text_table()
    finally:
        session.close()

    print(f"\nFilas por fuente: {by_source}")
    print(f"Duplicados saltados: {skipped}")
    print(f"Productos insertados: {total}")
    print(f"Ingredientes enriquecidos: {added} (+{updated} sustratos)")
    print(f"Vinculos de uso entre productos: {uses}")
    print("Base de datos lista en data/build.db")


def main():
    parser = argparse.ArgumentParser(description="Construye la base de datos de conservas del mundo")
    parser.add_argument("--sources", nargs="+", default=SOURCES, choices=SOURCES)
    parser.add_argument("--reset", action="store_true", help="Recrea la base de datos desde cero")
    args = parser.parse_args()
    try:
        run(args.sources, reset=args.reset)
    except KeyboardInterrupt:
        print("\nInterrumpido.")
        sys.exit(1)


if __name__ == "__main__":
    main()
