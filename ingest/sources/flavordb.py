"""FlavorDB (roadmap 2.12): moléculas de sabor por ingrediente.

Descarga las ~936 entidades de FlavorDB (cosylab.iiitd.edu.in) iterando IDs,
cachea el volcado completo y vincula moléculas a nuestros ingredientes
canónicos por coincidencia exacta o por contención de palabra.
"""

import json
import re
import time
from pathlib import Path

import httpx
from app.db import models
from ingest.normalize import normalize_name

BASE = "https://cosylab.iiitd.edu.in/flavordb"
RAW_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "flavordb_entities.json"
MAX_ID = 1000
CONSECUTIVE_MISSES = 20
_DELAY = 0.25


def fetch_all_entities() -> list[dict]:
    """Itera IDs hasta agotar; cachea el resultado combinado."""
    if RAW_PATH.exists():
        return json.loads(RAW_PATH.read_text(encoding="utf-8"))

    entities: list[dict] = []
    misses = 0
    headers = {"User-Agent": "ConservasDelMundo/0.2"}
    with httpx.Client(headers=headers, timeout=40, follow_redirects=True) as client:
        for entity_id in range(1, MAX_ID + 1):
            try:
                resp = client.get(f"{BASE}/entities_json", params={"id": entity_id})
            except httpx.HTTPError:
                misses += 1
                if misses >= CONSECUTIVE_MISSES:
                    break
                continue
            if resp.status_code != 200:
                misses += 1
                if misses >= CONSECUTIVE_MISSES:
                    break
                time.sleep(_DELAY)
                continue
            misses = 0
            data = resp.json()
            if isinstance(data, dict) and data.get("entity_alias_readable"):
                entities.append(data)
            time.sleep(_DELAY)

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_text(json.dumps(entities), encoding="utf-8")
    return entities


def _tokens(name: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", name.lower()) if len(t) > 2}


def match_ingredient(fdb_names: list[str], ingredient_names: dict[str, str]) -> str | None:
    """Devuelve el nombre canónico de nuestro ingrediente que corresponde a la
    entidad FlavorDB (alias legible + sinónimos), o None.

    ingredient_names: nombre_normalizado -> nombre_canónico.
    """
    fdb_norm = {normalize_name(n) for n in fdb_names if n}
    for fn in fdb_norm:
        if fn in ingredient_names:
            return ingredient_names[fn]
    # Contención por tokens completos (p.ej. 'cow milk' -> 'milk').
    fdb_tokens = set()
    for n in fdb_names:
        fdb_tokens |= _tokens(n)
    best: tuple[int, str] | None = None
    for norm, canonical in ingredient_names.items():
        itokens = _tokens(norm)
        if itokens and itokens <= fdb_tokens:
            score = len(itokens)
            if best is None or score > best[0]:
                best = (score, canonical)
    return best[1] if best else None


def parse_entities_to_pairs(
    entities: list[dict], our_norm_names: set[str]
) -> list[tuple[str, str, int | None]]:
    """Función pura: entidades FlavorDB -> [(ingrediente_norm, molécula, pubchem_id)].

    Solo entidades cuyo nombre/sinónimo mapea a un ingrediente nuestro.
    """
    pairs: list[tuple[str, str, int | None]] = []
    names_map = {n: n for n in our_norm_names}
    for entity in entities:
        readable = entity.get("entity_alias_readable") or ""
        candidates = [readable] + list(entity.get("entity_alias_synonyms") or [])
        matched_norm = None
        for cand in candidates:
            m = match_ingredient([cand], names_map)
            if m:
                matched_norm = normalize_name(m)
                break
        if matched_norm is None:
            continue
        for mol in entity.get("molecules", []):
            name = (mol.get("common_name") or "").strip()
            if not name:
                continue
            pairs.append((matched_norm, name, mol.get("pubchem_id")))
    return pairs


def enrich_ingredient_molecules(session, *, max_per_ingredient: int = 80) -> tuple[int, int]:
    """Vincula moléculas a ingredientes que aún no tengan ninguna.

    Devuelve (ingredientes_enriquecidos, vínculos_creados).
    """
    entities = fetch_all_entities()

    ingredients = session.query(models.Ingredient).all()
    by_norm: dict[str, models.Ingredient] = {}
    for ing in ingredients:
        by_norm[normalize_name(ing.name)] = ing

    existing_pairs = {
        (row[0], row[1])
        for row in session.query(
            models.IngredientFlavorMolecule.ingredient_id,
            models.IngredientFlavorMolecule.molecule_id,
        ).all()
    }
    molecules_by_key: dict[tuple[str, int | None], int] = {
        (normalize_name(m.name), m.pubchem_id): m.id
        for m in session.query(models.FlavorMolecule).all()
    }

    enriched = 0
    created = 0
    for entity in entities:
        readable = entity.get("entity_alias_readable") or ""
        synonyms = entity.get("entity_alias_synonyms") or []
        candidates = [readable] + list(synonyms)
        ingredient = None
        for cand in candidates:
            matched = match_ingredient(
                [cand], {k: v.name for k, v in by_norm.items()}
            )
            if matched:
                ingredient = by_norm[normalize_name(matched)]
                break
        if ingredient is None:
            continue

        already = {
            mid
            for (iid, mid) in existing_pairs
            if iid == ingredient.id
        }
        added = 0
        for mol in entity.get("molecules", []):
            name = (mol.get("common_name") or "").strip()
            pubchem = mol.get("pubchem_id")
            key = (normalize_name(name), pubchem)
            mid = molecules_by_key.get(key)
            if mid is None:
                molecule = models.FlavorMolecule(name=name, pubchem_id=pubchem)
                session.add(molecule)
                session.flush()
                molecules_by_key[key] = molecule.id
                mid = molecule.id
            if mid in already or (ingredient.id, mid) in existing_pairs:
                continue
            session.execute(
                models.IngredientFlavorMolecule.__table__.insert().values(
                    ingredient_id=ingredient.id, molecule_id=mid
                )
            )
            existing_pairs.add((ingredient.id, mid))
            created += 1
            added += 1
            if added >= max_per_ingredient:
                break
        if added:
            enriched += 1
    session.commit()
    return enriched, created

