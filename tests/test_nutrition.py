from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import models
from ingest.sources import usda

_SAMPLE_FOOD = {
    "fdcId": 2709775,
    "description": "Cabbage, red, raw",
    "foodNutrients": [
        {"nutrientId": 1003, "nutrientName": "Protein", "value": 1.24},
        {"nutrientId": 1004, "nutrientName": "Total lipid (fat)", "value": 0.21},
        {"nutrientId": 1005, "nutrientName": "Carbohydrate, by difference", "value": 6.79},
        {"nutrientId": 1008, "nutrientName": "Energy", "value": 34},
        {"nutrientId": 1079, "nutrientName": "Fiber, total dietary", "value": 2.1},
        {"nutrientId": 1087, "nutrientName": "Calcium, Ca", "value": 31},
        {"nutrientId": 1089, "nutrientName": "Iron, Fe", "value": 0},
        {"nutrientId": 1092, "nutrientName": "Potassium, K", "value": 269},
        {"nutrientId": 1093, "nutrientName": "Sodium, Na", "value": 12},
        {"nutrientId": 1095, "nutrientName": "Zinc, Zn", "value": 0.24},
        {"nutrientId": 1162, "nutrientName": "Vitamin C, total ascorbic acid", "value": 53.9},
    ],
}


def _ingredient_id(client, name):
    ingredients = client.get("/ingredients").json()
    return next(i["id"] for i in ingredients if i["name"] == name)


def _add_nutrition(client, tmp_path, ingredient_id, **kwargs):
    engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    testing = sessionmaker(bind=engine)
    session = testing()
    try:
        session.add(models.NutritionData(ingredient_id=ingredient_id, fdc_id="2709775", **kwargs))
        session.commit()
    finally:
        session.close()


def test_nutrition_no_data_returns_null(client):
    cabbage_id = _ingredient_id(client, "cabbage")
    resp = client.get(f"/ingredients/{cabbage_id}/nutrition")
    assert resp.status_code == 200
    assert resp.json() is None


def test_nutrition_with_data(client, tmp_path):
    cabbage_id = _ingredient_id(client, "cabbage")
    _add_nutrition(
        client,
        tmp_path,
        cabbage_id,
        calories=34,
        protein_g=1.24,
        sodium_mg=12,
        vitamin_c_mg=53.9,
    )
    resp = client.get(f"/ingredients/{cabbage_id}/nutrition")
    assert resp.status_code == 200
    data = resp.json()
    assert data["fdc_id"] == "2709775"
    assert data["calories"] == 34
    assert data["protein_g"] == 1.24
    assert data["sodium_mg"] == 12
    assert data["vitamin_c_mg"] == 53.9
    assert resp.headers["Cache-Control"] == "public, max-age=86400"


def test_nutrition_ingredient_not_found(client):
    resp = client.get("/ingredients/99999/nutrition")
    assert resp.status_code == 404


def test_pick_nutrients_maps_ids():
    data = usda.pick_nutrients(_SAMPLE_FOOD)
    assert data["calories"] == 34
    assert data["protein_g"] == 1.24
    assert data["fat_g"] == 0.21
    assert data["carbs_g"] == 6.79
    assert data["fiber_g"] == 2.1
    assert data["calcium_mg"] == 31
    assert data["iron_mg"] == 0
    assert data["potassium_mg"] == 269
    assert data["sodium_mg"] == 12
    assert data["zinc_mg"] == 0.24
    assert data["vitamin_c_mg"] == 53.9


def test_pick_nutrients_missing_is_none():
    food = {"fdcId": 1, "foodNutrients": [{"nutrientId": 1003, "value": 2.0}]}
    data = usda.pick_nutrients(food)
    assert data["protein_g"] == 2.0
    assert data["calories"] is None
    assert data["zinc_mg"] is None


def test_search_food_picks_best_match():
    import httpx

    def handler(request):
        return httpx.Response(
            200,
            json={
                "foods": [
                    {"fdcId": 1, "description": "Cabbage, cooked", "foodNutrients": []},
                    {"fdcId": 2, "description": "Cabbage, red, raw", "foodNutrients": []},
                    {"fdcId": 3, "description": "Potato", "foodNutrients": []},
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    food = usda.search_food(client, "DEMO_KEY", "cabbage raw", "Survey (FNDDS)")
    assert food["fdcId"] == 2
