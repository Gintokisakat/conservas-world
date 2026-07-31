import argparse
import sys

from app.db.database import SessionLocal, init_db
from ingest.normalize import normalize_name

SOURCES = ["fermdb", "wikipedia", "openfoodfacts", "wikidata"]


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
            else:
                raise ValueError(f"Fuente desconocida: {source}")
            print(f"Ingiriendo fuente: {source} ...", flush=True)
            if source == "fermdb":
                records = fermdb.load_source()
            elif source == "wikipedia":
                records = wikipedia.load_source()
            elif source == "openfoodfacts":
                records = openfoodfacts.load_source()
            else:
                records = wikidata.load_source()
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
        added, updated = loader.enrich_ingredients(session)
        uses = loader.build_product_uses(session)
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
