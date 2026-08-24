"""Recetas comunitarias (roadmap 4.3)."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_user
from app.db import models
from app.db.database import get_session
from app.schemas import (
    RecipeAuthor,
    RecipeCreate,
    RecipeOut,
    RecipesFeed,
    RecipeUpdate,
)

router = APIRouter(tags=["recipes"])


def _parse_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _recipe_out(
    recipe: models.Recipe, user: models.User | None, voted: bool = False
) -> RecipeOut:
    return RecipeOut(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        steps=_parse_list(recipe.steps_json),
        ingredients=_parse_list(recipe.ingredients_json),
        difficulty=recipe.difficulty,
        prep_time_min=recipe.prep_time_min,
        votes=recipe.votes,
        created_at=recipe.created_at,
        author=RecipeAuthor(id=recipe.user_id, username=recipe.user.username),
        product_id=recipe.product_id,
        mine=user is not None and recipe.user_id == user.id,
        voted=voted,
    )


def _load_recipe(session: Session, recipe_id: int) -> models.Recipe:
    recipe = session.get(models.Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe


def _has_voted(session: Session, recipe_id: int, user: models.User | None) -> bool:
    if user is None:
        return False
    return session.get(models.RecipeVote, (recipe_id, user.id)) is not None


@router.get("/recipes", response_model=RecipesFeed)
def list_recipes(
    q: str | None = Query(default=None, description="Buscar en título/descripción"),
    difficulty: str | None = Query(default=None, pattern="^(facil|media|dificil)$"),
    product_id: int | None = None,
    sort: str = Query(default="votes", pattern="^(votes|recent)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: models.User | None = Depends(get_optional_user),
    session: Session = Depends(get_session),
):
    """Feed de recetas comunitarias con búsqueda y filtros."""
    query = select(models.Recipe).join(models.User, models.Recipe.user_id == models.User.id)
    count_q = select(func.count()).select_from(models.Recipe)
    if q:
        cond = models.Recipe.title.ilike(f"%{q}%") | models.Recipe.description.ilike(f"%{q}%")
        query = query.where(cond)
        count_q = count_q.where(cond)
    if difficulty:
        query = query.where(models.Recipe.difficulty == difficulty)
        count_q = count_q.where(models.Recipe.difficulty == difficulty)
    if product_id:
        query = query.where(models.Recipe.product_id == product_id)
        count_q = count_q.where(models.Recipe.product_id == product_id)
    total = session.execute(count_q).scalar_one()
    order = (
        models.Recipe.votes.desc()
        if sort == "votes"
        else models.Recipe.created_at.desc()
    )
    rows = session.execute(
        query.order_by(order, models.Recipe.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).scalars().all()
    items = []
    for r in rows:
        items.append(_recipe_out(r, user, voted=_has_voted(session, r.id, user)))
    return RecipesFeed(total=total, items=items)


@router.post("/recipes", response_model=RecipeOut, status_code=201)
def create_recipe(
    body: RecipeCreate,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if body.product_id is not None:
        product = session.get(models.Product, body.product_id)
        if product is None or product.status == "discarded":
            raise HTTPException(status_code=404, detail="Producto no encontrado")
    recipe = models.Recipe(
        user_id=user.id,
        product_id=body.product_id,
        title=body.title.strip(),
        description=body.description,
        steps_json=json.dumps(body.steps, ensure_ascii=False),
        ingredients_json=json.dumps(body.ingredients, ensure_ascii=False),
        difficulty=body.difficulty,
        prep_time_min=body.prep_time_min,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return _recipe_out(recipe, user)


@router.get("/recipes/{recipe_id}", response_model=RecipeOut)
def get_recipe(
    recipe_id: int,
    user: models.User | None = Depends(get_optional_user),
    session: Session = Depends(get_session),
):
    recipe = _load_recipe(session, recipe_id)
    return _recipe_out(recipe, user, voted=_has_voted(session, recipe.id, user))


def _load_own_recipe(recipe_id: int, user: models.User, session: Session) -> models.Recipe:
    recipe = _load_recipe(session, recipe_id)
    if recipe.user_id != user.id:
        raise HTTPException(status_code=403, detail="No es tu receta")
    return recipe


@router.put("/recipes/{recipe_id}", response_model=RecipeOut)
def update_recipe(
    recipe_id: int,
    body: RecipeUpdate,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    recipe = _load_own_recipe(recipe_id, user, session)
    recipe.title = body.title.strip()
    recipe.description = body.description
    recipe.steps_json = json.dumps(body.steps, ensure_ascii=False)
    recipe.ingredients_json = json.dumps(body.ingredients, ensure_ascii=False)
    recipe.difficulty = body.difficulty
    recipe.prep_time_min = body.prep_time_min
    if body.product_id != recipe.product_id and body.product_id is not None:
        product = session.get(models.Product, body.product_id)
        if product is None or product.status == "discarded":
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        recipe.product_id = body.product_id
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return _recipe_out(recipe, user)


@router.delete("/recipes/{recipe_id}", status_code=204)
def delete_recipe(
    recipe_id: int,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    recipe = _load_own_recipe(recipe_id, user, session)
    session.delete(recipe)
    session.commit()


@router.post("/recipes/{recipe_id}/vote", response_model=RecipeOut)
def vote_recipe(
    recipe_id: int,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Vota una receta (+1). Un voto por usuario."""
    recipe = _load_recipe(session, recipe_id)
    if _has_voted(session, recipe.id, user):
        raise HTTPException(status_code=409, detail="Ya votaste esta receta")
    session.add(models.RecipeVote(recipe_id=recipe.id, user_id=user.id))
    recipe.votes += 1
    session.commit()
    session.refresh(recipe)
    return _recipe_out(recipe, user, voted=True)


@router.delete("/recipes/{recipe_id}/vote", response_model=RecipeOut)
def unvote_recipe(
    recipe_id: int,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Retira el voto del usuario (-1)."""
    recipe = _load_recipe(session, recipe_id)
    vote = session.get(models.RecipeVote, (recipe.id, user.id))
    if vote is None:
        raise HTTPException(status_code=404, detail="No habías votado")
    session.delete(vote)
    recipe.votes = max(0, recipe.votes - 1)
    session.commit()
    session.refresh(recipe)
    return _recipe_out(recipe, user, voted=False)
