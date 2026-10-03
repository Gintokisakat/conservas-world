#!/usr/bin/env python
"""Comparación de relevancia entre backends (P0-2/P0-3). Log-only."""
import json
from pathlib import Path

DATA = Path("tests/data/search_queries.json")
OUT = Path("data/search_relevance_dual.json")


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Falta {DATA}")
    queries = json.loads(DATA.read_text())
    results = {"meta": {"queries": len(queries)}, "results": []}
    for q in queries:
        results["results"].append(
            {
                "query": q["query"],
                "desc": q.get("desc", ""),
                "sqlite_top10": [],
                "pg_top10": [],
                "jaccard@10": None,
                "kendall@10": None,
            }
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2))
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()
