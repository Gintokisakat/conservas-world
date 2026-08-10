import argparse
import os
import time

import httpx
from app.db import models
from app.db.database import SessionLocal, init_db

FDC_API = "https://api.nal.usda.gov/fdc/v1"

# nutrientId -> columna del modelo NutritionData (valores por 100 g).
NUTRIENTS = {
    1008: "calories",
    2047: "calories",
    1003: "protein_g",
    1004: "fat_g",
    1005: "carbs_g",
    1079: "fiber_g",
    1093: "sodium_mg",
    1092: "potassium_mg",
    1162: "vitamin_c_mg",
    1089: "iron_mg",
    1087: "calcium_mg",
    1095: "zinc_mg",
}

HEADERS = {"User-Agent": "conservas-world/0.2 (research database seed)"}
DEMO_LIMIT_HOUR = 50
DEMO_SLEEP = (3600 // DEMO_LIMIT_HOUR) + 1


def get_api_key() -> str:
    return os.environ.get("USDA_API_KEY") or "DEMO_KEY"


def _score(description: str, tokens: list[str]) -> int:
    desc = description.lower()
    return sum(1 for t in tokens if t in desc)


def search_food(client: httpx.Client, api_key: str, query: str, data_type: str) -> dict | None:
    """Busca el alimento mas parecido en la USDA FDC y devuelve el JSON del food."""
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            r = client.get(
                f"{FDC_API}/foods/search",
                params={
                    "api_key": api_key,
                    "query": query,
                    "dataType": data_type,
                    "pageSize": 10,
                    "pageNumber": 1,
                },
                headers=HEADERS,
                timeout=20,
            )
            if r.status_code == 429 or r.status_code >= 500:
                last_error = RuntimeError(f"HTTP {r.status_code}")
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code != 200:
                r.raise_for_status()
            data = r.json()
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(2 * (attempt + 1))
    else:
        raise RuntimeError(f"USDA API fallo tras reintentos: {last_error}")
    foods = data.get("foods", [])
    if not foods:
        return None
    tokens = [t for t in query.split() if t]
    best = max(foods, key=lambda f: _score(f.get("description", ""), tokens))
    return best


def pick_nutrients(food: dict) -> dict:
    values: dict[str, float | None] = {col: None for col in set(NUTRIENTS.values())}
    for nutrient in food.get("foodNutrients", []):
        col = NUTRIENTS.get(nutrient.get("nutrientId"))
        if col is not None:
            value = nutrient.get("value")
            if value is not None and (values[col] is None or col == "calories"):
                values[col] = float(value)
    return values


def fetch_ingredient(client: httpx.Client, api_key: str, name: str) -> dict | None:
    """Devuelve dict del modelo NutritionData para el ingrediente, o None si no hay match."""
    for data_type in ("Survey (FNDDS)", "Foundation", "SR Legacy"):
        food = search_food(client, api_key, name, data_type)
        if food:
            return {"fdc_id": str(food["fdcId"]), **pick_nutrients(food)}
    return None


def load_nutrition(limit: int = 50, api_key: str | None = None) -> tuple[int, int]:
    """Rellena nutrition_data para ingredientes que aun no la tienen.

    Con DEMO_KEY se limita a `limit` ingredientes y se espera ~72 s entre
    llamadas (50 req/h). Con USDA_API_KEY real (1000 req/h) el delay se omite.
    """
    api_key = api_key or get_api_key()
    is_demo = api_key == "DEMO_KEY"

    init_db()
    session = SessionLocal()
    try:
        pending = (
            session.query(models.Ingredient)
            .outerjoin(models.NutritionData)
            .filter(models.NutritionData.id.is_(None))
            .order_by(models.Ingredient.name)
            .limit(limit)
            .all()
        )
        if not pending:
            print("Todos los ingredientes ya tienen datos de nutricion.")
            return 0, 0

        filled = 0
        errors = 0
        with httpx.Client() as client:
            for i, ingredient in enumerate(pending, 1):
                print(f"[{i}/{len(pending)}] {ingredient.name} ...", flush=True)
                try:
                    data = fetch_ingredient(client, api_key, ingredient.name)
                    if data is None:
                        print(f"  sin match: {ingredient.name}")
                    else:
                        existing = (
                            session.query(models.NutritionData)
                            .filter(models.NutritionData.ingredient_id == ingredient.id)
                            .first()
                        )
                        if existing is None:
                            session.add(models.NutritionData(ingredient_id=ingredient.id, **data))
                        else:
                            for k, v in data.items():
                                setattr(existing, k, v)
                        session.commit()
                        filled += 1
                        print(f"  ok fdcId={data['fdc_id']}")
                except Exception as exc:  # noqa: BLE001
                    session.rollback()
                    errors += 1
                    print(f"  error: {exc}")
                if is_demo and i < len(pending):
                    time.sleep(DEMO_SLEEP)
        return filled, errors
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Rellena datos de nutricion (USDA FoodData Central) para los ingredientes"
    )
    parser.add_argument("--limit", type=int, default=50, help="Max ingredientes a procesar")
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key de USDA (si se omite, se usa $USDA_API_KEY o DEMO_KEY)",
    )
    args = parser.parse_args()
    filled, errors = load_nutrition(limit=args.limit, api_key=args.api_key)
    print(f"\nIngredientes con nutricion: {filled} (+{errors} errores)")


if __name__ == "__main__":
    main()
