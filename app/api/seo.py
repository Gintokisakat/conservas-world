"""SEO y structured data (4.9): sitemap.xml, robots.txt y SSR del detalle de producto.

El detalle de producto se renderiza server-side en /p/{id} con meta Open Graph/Twitter,
canonical y JSON-LD Schema.org (Product/Recipe), enlazando a la SPA para humanos.
"""

import html
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.api.routes import _load_product
from app.db.database import get_session
from app.db.models import Product
from app.services.flavors import flavor_profile

router = APIRouter()

SITE_URL = "https://conservas-world.example"
SPA_BASE = "/"


def _json_ld_product(p: Product) -> dict:
    countries = [c.name for c in p.countries]
    ingredients = [i.name for i in p.ingredients]
    profile = flavor_profile(p.name, p.method, ingredients)
    top_axes = sorted(profile.items(), key=lambda kv: -kv[1])[:3]
    keywords = ", ".join(ax for ax, v in top_axes if v > 0) or "fermentación"
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p.name,
        "description": p.description or p.method or p.name,
        "image": p.image_url,
        "url": f"{SITE_URL}/p/{p.id}",
        "sku": f"conservas-{p.id}",
        "brand": {"@type": "Brand", "name": "Conservas del Mundo"},
        "keywords": keywords,
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "método", "value": p.method or ""},
            {"@type": "PropertyValue", "name": "tiempo de fermentación", "value": p.fermentation_time or ""},
            {"@type": "PropertyValue", "name": "vida útil", "value": p.storage_life or ""},
        ],
        "countryOfOrigin": countries,
        "ingredients": ingredients,
        "manufacturer": {"@type": "Organization", "name": "Conservas del Mundo"},
    }


def _render_product_page(p: Product, lang: str = "es") -> str:
    name = html.escape(p.name)
    desc = html.escape(p.description or p.method or "")
    img = html.escape(p.image_url or "") if p.image_url else ""
    ingredients = ", ".join(html.escape(i.name) for i in p.ingredients)
    countries = ", ".join(html.escape(c.name) for c in p.countries)
    method = html.escape(p.method or "")
    ftime = html.escape(p.fermentation_time or "")
    storage = html.escape(p.storage_life or "")
    og_img = img or f"{SITE_URL}/static/img/og-default.png"

    meta = [
        '<meta property="og:type" content="product">',
        f'<meta property="og:title" content="{name} — Conservas del Mundo">',
        f'<meta property="og:description" content="{desc[:200]}">',
        f'<meta property="og:image" content="{og_img}">',
        f'<meta property="og:url" content="{SITE_URL}/p/{p.id}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{name}">',
        f'<meta name="twitter:description" content="{desc[:200]}">',
        f'<meta name="twitter:image" content="{og_img}">',
        f'<link rel="canonical" href="{SITE_URL}/p/{p.id}">',
    ]
    json_ld = json.dumps(_json_ld_product(p), ensure_ascii=False)
    spa_url = f"{SPA_BASE}#/product/{p.id}"

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{name} — Conservas del Mundo</title>
<meta name="description" content="{desc[:200]}">
{chr(10).join(meta)}
<script type="application/ld+json">{json_ld}</script>
</head>
<body>
<main>
<h1>{name}</h1>
<img src="{og_img}" alt="{name}" width="400">
<p>{desc}</p>
<dl>
<dt>Método</dt><dd>{method or "—"}</dd>
<dt>Tiempo de fermentación</dt><dd>{ftime or "—"}</dd>
<dt>Vida útil</dt><dd>{storage or "—"}</dd>
<dt>Ingredientes</dt><dd>{ingredients or "—"}</dd>
<dt>País de origen</dt><dd>{countries or "—"}</dd>
</dl>
<a href="{spa_url}">Abrir en la aplicación →</a>
</main>
</body>
</html>"""


@router.get("/sitemap.xml", response_class=Response, include_in_schema=False)
def sitemap(session: Session = Depends(get_session)) -> Response:
    import sqlalchemy as sa

    ids = session.execute(sa.select(Product.id).where(Product.status.in_(["imported", "reviewed"]))).scalars().all()
    urls = [f"{SITE_URL}/p/{pid}" for pid in ids]
    urls += [f"{SITE_URL}/", f"{SITE_URL}/#/glossary", f"{SITE_URL}/#/timeline"]
    body = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
    for u in urls:
        body.append(f"  <url><loc>{html.escape(u)}</loc></url>")
    body.append("</urlset>")
    return Response("\n".join(body), media_type="application/xml")


@router.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
def robots() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )


@router.get("/p/{product_id}", response_class=HTMLResponse, include_in_schema=False)
def product_page(product_id: int, session: Session = Depends(get_session)) -> HTMLResponse:
    try:
        p = _load_product(session, product_id)
    except HTTPException:
        raise
    page = _render_product_page(p)
    return HTMLResponse(page)


@router.get("/.well-known/structured-data", include_in_schema=False)
def structured_data_lint(session: Session = Depends(get_session)) -> dict:
    from sqlalchemy import select

    from app.db import models

    ids = session.execute(select(models.Product.id).limit(5)).scalars().all()
    products = [_load_product(session, pid) for pid in ids]
    return {"products": [_json_ld_product(p) for p in products]}