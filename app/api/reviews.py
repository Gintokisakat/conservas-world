"""Reseñas de productos (roadmap 4.2)."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_user
from app.db import models
from app.db.database import get_session
from app.schemas import ReviewCreate, ReviewOut, ReviewsOut, ReviewUpdate

router = APIRouter(tags=["reviews"])


def _review_out(review: models.Review, user: models.User | None) -> ReviewOut:
    mine = user is not None and review.user_id == user.id
    return ReviewOut(
        id=review.id,
        product_id=review.product_id,
        rating=review.rating,
        text=review.text,
        flagged=review.flagged,
        created_at=review.created_at,
        updated_at=review.updated_at,
        mine=mine,
    )


def _load_product(session: Session, product_id: int) -> models.Product:
    product = session.get(models.Product, product_id)
    if product is None or product.status == "discarded":
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.get("/products/{product_id}/reviews", response_model=ReviewsOut)
def list_reviews(
    product_id: int,
    user: models.User | None = Depends(get_optional_user),
    session: Session = Depends(get_session),
):
    """Reseñas del producto con promedio; marca `mine` si hay token."""
    _load_product(session, product_id)
    rows = session.execute(
        select(models.Review)
        .where(models.Review.product_id == product_id, models.Review.flagged.is_(False))
        .order_by(models.Review.created_at.desc())
    ).scalars().all()
    average = round(sum(r.rating for r in rows) / len(rows), 2) if rows else None
    return ReviewsOut(total=len(rows), average=average, items=[_review_out(r, user) for r in rows])


@router.post("/products/{product_id}/reviews", response_model=ReviewOut, status_code=201)
def create_review(
    product_id: int,
    body: ReviewCreate,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Crea la reseña del usuario para el producto (una por usuario y producto)."""
    _load_product(session, product_id)
    existing = session.execute(
        select(models.Review).where(
            models.Review.user_id == user.id, models.Review.product_id == product_id
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Ya reseñaste este producto")
    review = models.Review(
        user_id=user.id, product_id=product_id, rating=body.rating, text=body.text
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    out = _review_out(review, user)
    out.mine = True
    return out


def _load_own_review(review_id: int, user: models.User, session: Session) -> models.Review:
    review = session.get(models.Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="No es tu reseña")
    return review


@router.put("/reviews/{review_id}", response_model=ReviewOut)
def update_review(
    review_id: int,
    body: ReviewUpdate,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    review = _load_own_review(review_id, user, session)
    review.rating = body.rating
    review.text = body.text
    review.updated_at = datetime.now(UTC).replace(tzinfo=None)
    session.add(review)
    session.commit()
    session.refresh(review)
    return _review_out(review, user)


@router.delete("/reviews/{review_id}", status_code=204)
def delete_review(
    review_id: int,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    review = _load_own_review(review_id, user, session)
    session.delete(review)
    session.commit()


@router.post("/reviews/{review_id}/flag", status_code=204)
def flag_review(
    review_id: int,
    user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Marca una reseña como reportada (moderación básica)."""
    review = session.get(models.Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    review.flagged = True
    session.add(review)
    session.commit()
