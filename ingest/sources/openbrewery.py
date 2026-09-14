"""Integración de Open Brewery DB para cervecerías y sidrerías artesanales (roadmap 2.7)."""

from app.db import models
from sqlalchemy import select
from sqlalchemy.orm import Session

# Curated craft breweries / fermenteries fallback seed data
CURATED_BREWERIES = [
    {
        "brewery_id": "antares-mar-del-plata",
        "name": "Cervecería Antares",
        "brewery_type": "micro",
        "country": "Argentina",
        "state_province": "Buenos Aires",
        "city": "Mar del Plata",
        "address": "12 de Octubre 7749",
        "latitude": -38.0345,
        "longitude": -57.5645,
        "website_url": "https://www.cervezaantares.com",
        "phone": "+542234830154",
    },
    {
        "brewery_id": "baeren-brewery-morioka",
        "name": "Baeren Brewery",
        "brewery_type": "micro",
        "country": "Japón",
        "state_province": "Iwate",
        "city": "Morioka",
        "address": "1-1-1 Kitayama",
        "latitude": 39.7153,
        "longitude": 141.1558,
        "website_url": "https://www.baerenbier.co.jp",
        "phone": "+81196060900",
    },
    {
        "brewery_id": "cantillon-brussels",
        "name": "Brasserie Cantillon (Gueuze & Lambic)",
        "brewery_type": "micro",
        "country": "Bélgica",
        "state_province": "Brussels",
        "city": "Brussels",
        "address": "Rue Gheude 56",
        "latitude": 50.8415,
        "longitude": 4.3351,
        "website_url": "https://www.cantillon.be",
        "phone": "+3225214928",
    },
    {
        "brewery_id": "sierra-nevada-chico",
        "name": "Sierra Nevada Brewing Co.",
        "brewery_type": "regional",
        "country": "Estados Unidos",
        "state_province": "California",
        "city": "Chico",
        "address": "1075 E 20th St",
        "latitude": 39.7247,
        "longitude": -121.8157,
        "website_url": "https://sierranevada.com",
        "phone": "+15308933537",
    },
    {
        "brewery_id": "sidra-trabanco-gijon",
        "name": "Sidra Trabanco (Sidrería artesana)",
        "brewery_type": "cidery",
        "country": "España",
        "state_province": "Asturias",
        "city": "Gijón",
        "address": "Carretera Lavandera 325",
        "latitude": 43.4752,
        "longitude": -5.6588,
        "website_url": "https://www.sidratrabanco.com",
        "phone": "+34985136462",
    },
]


def seed_breweries(session: Session) -> int:
    """Siembra cervecerías y sidrerías artesanales en la base de datos de forma idempotente."""
    added = 0
    for data in CURATED_BREWERIES:
        existing = session.scalars(
            select(models.Brewery).where(models.Brewery.brewery_id == data["brewery_id"])
        ).first()
        if not existing:
            b = models.Brewery(**data)
            session.add(b)
            added += 1
    if added:
        session.commit()
    return added
