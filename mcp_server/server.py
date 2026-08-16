"""Servidor MCP (Model Context Protocol) de conservas-world (roadmap 3.10).

Expone la base de datos como herramientas MCP consumibles por agentes de IA:
búsqueda de productos, detalle, ingredientes, temporizador de fermentación y
lookup de código de barras vía Open Food Facts.

Ejecutar:  uv run python -m mcp_server.server
Testear:   uv run python -m mcp_server.server (cliente MCP de Claude, etc.)
Se sirve por stdio con `mcp.server.stdio`; se usa el SDK oficial `mcp`
(imports como `from mcp import types`), sin la API FastMCP retirada en v2.
"""

import json
import re
import unicodedata
from typing import Any

import httpx
from app.db import models
from app.db.database import SessionLocal
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.request_state import ServerRequestContext
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

SERVER_NAME = "conservas-world"
SERVER_VERSION = "0.1.0"

# Patrones para parsear tiempos de fermentación en días.
_TIME_PATTERNS = [
    (re.compile(r"(\d+)\s*[-–]\s*(\d+)\s*(d[íi]as?|dias?|semanas?|meses?|a[ñn]os?)", re.I), 1),
    (re.compile(r"(\d+)\s*(d[íi]as?|dias?|semanas?|meses?|a[ñn]os?)", re.I), 2),
]
_UNIT_DAYS = {
    "dia": 1,
    "dias": 1,
    "semana": 7,
    "semanas": 7,
    "mes": 30,
    "meses": 30,
    "ano": 365,
    "anos": 365,
}


def _norm_unit(unit: str) -> str:
    unit = unit.lower()
    return "".join(c for c in unicodedata.normalize("NFD", unit) if unicodedata.category(c) != "Mn")


def _parse_days(text: str | None) -> tuple[int, int] | None:
    """Devuelve (min_days, max_days) aproximados a partir del texto de fermentación."""
    if not text:
        return None
    for pattern, kind in _TIME_PATTERNS:
        m = pattern.search(text)
        if m:
            unit = _norm_unit(m.group(3) if kind == 1 else m.group(2))
            mult = _UNIT_DAYS.get(unit, 1)
            if kind == 1:
                return (int(m.group(1)) * mult, int(m.group(2)) * mult)
            value = int(m.group(1))
            return (value * mult, value * mult)
    return None


def _product_detail(session, product_id: int) -> dict | None:
    product = session.execute(
        select(models.Product)
        .options(
            selectinload(models.Product.aliases),
            selectinload(models.Product.countries),
            selectinload(models.Product.ingredients),
            selectinload(models.Product.categories),
            selectinload(models.Product.microbes),
            selectinload(models.Product.references),
            selectinload(models.Product.uses).selectinload(models.ProductUse.used_product),
            selectinload(models.Product.dairy),
            selectinload(models.Product.metagenome),
        )
        .where(models.Product.id == product_id)
    ).scalar_one_or_none()
    if product is None:
        return None
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "method": product.method,
        "fermentation_time": product.fermentation_time,
        "storage_life": product.storage_life,
        "status": product.status,
        "source_tag": product.source_tag,
        "substrate": product.substrate,
        "image_url": product.image_url,
        "aliases": [a.name for a in product.aliases],
        "countries": [{"name": c.name, "continent": c.continent} for c in product.countries],
        "ingredients": [i.name for i in product.ingredients],
        "categories": [c.code for c in product.categories],
        "microbes": [m.name for m in product.microbes],
        "references": [{"title": r.title, "url": r.url, "doi": r.doi} for r in product.references],
        "uses": sorted({u.used_product.name for u in product.uses if u.used_product}),
        "dairy": (
            {
                "classification": product.dairy.classification,
                "country": product.dairy.country,
                "region": product.dairy.region,
                "milk_type": product.dairy.milk_type,
                "treatment": product.dairy.treatment,
                "ripening": product.dairy.ripening,
                "geographical_indication": bool(product.dairy.geographical_indication),
                "microbiota": _json_list(product.dairy.microbiota_json),
            }
            if product.dairy
            else None
        ),
        "metagenome": (
            {
                "subtype": product.metagenome.subtype,
                "sample_count": product.metagenome.sample_count,
                "taxa": _json_list(product.metagenome.taxa_json),
                "url": product.metagenome.url,
            }
            if product.metagenome
            else None
        ),
    }


def _json_list(raw: str | None) -> list:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def search_products(session, query: str, limit: int = 10) -> list[dict]:
    """Busca productos por nombre o descripción (subcadena), con categorías y países."""
    needle = query.strip().lower()
    rows = (
        session.execute(
            select(models.Product)
            .options(
                selectinload(models.Product.categories),
                selectinload(models.Product.countries),
            )
            .where(
                models.Product.status != "discarded",
                (func.lower(models.Product.name).contains(needle))
                | (func.lower(models.Product.description).contains(needle)),
            )
            .order_by(models.Product.name)
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": (p.description or "")[:200],
            "categories": [c.code for c in p.categories],
            "countries": [c.name for c in p.countries],
            "source_tag": p.source_tag,
        }
        for p in rows
    ]


def get_product(session, product_id: int) -> dict | None:
    """Devuelve el detalle completo de un producto por su id."""
    return _product_detail(session, product_id)


def get_ingredients(session, category: str | None = None, limit: int = 50) -> list[dict]:
    """Lista ingredientes canónicos (con nº de productos que los usan)."""
    query = (
        select(
            models.Ingredient.name,
            models.Ingredient.category,
            func.count(models.product_ingredient.c.product_id).label("n_products"),
        )
        .outerjoin(
            models.product_ingredient,
            models.product_ingredient.c.ingredient_id == models.Ingredient.id,
        )
        .group_by(models.Ingredient.id)
        .order_by(models.Ingredient.name)
    )
    if category:
        query = query.where(models.Ingredient.category == category)
    return [
        {"name": name, "category": cat, "n_products": n}
        for name, cat, n in session.execute(query.limit(limit)).all()
    ]


def get_timer(session, product_id: int, temp_c: int = 21) -> dict | None:
    """Devuelve el perfil de fermentación de un producto y días estimados.

    Usa un modelo Q10 simplificado: cada +10 °C duplica la velocidad de
    fermentación respecto a la temperatura de referencia de 21 °C."""
    product = session.execute(
        select(models.Product).where(models.Product.id == product_id)
    ).scalar_one_or_none()
    if product is None:
        return None
    base = _parse_days(product.fermentation_time)
    note = None
    days = None
    if base is None:
        note = "Sin rango de días declarado; usa los tiempos de referencia."
    else:
        lo, hi = base
        factor = 2 ** ((21 - temp_c) / 10)
        days = {"min": round(lo * factor), "max": round(hi * factor)}
    return {
        "product_id": product.id,
        "name": product.name,
        "fermentation_time": product.fermentation_time,
        "method": product.method,
        "storage_life": product.storage_life,
        "temperature_c": temp_c,
        "estimated_days": days,
        "model": "Q10 (x2 cada +10 °C, referencia 21 °C)",
        "note": note,
    }


def lookup_barcode(barcode: str) -> dict | None:
    """Busca un código de barras en Open Food Facts y, si el producto está en
    nuestra BD, lo indica con su id."""
    url = f"https://world.openfoodfacts.org/api/v3/product/{barcode}.json"
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        resp = client.get(url)
        if resp.status_code != 200:
            return None
        payload = resp.json()
    product = payload.get("product") or {}
    if not product:
        return None
    name = product.get("product_name") or product.get("product_name_es") or barcode
    session = SessionLocal()
    try:
        in_db = _find_by_name(session, name)
    finally:
        session.close()
    return {
        "barcode": barcode,
        "name": name,
        "brands": product.get("brands"),
        "categories": (product.get("categories_tags") or [])[:8],
        "image_url": product.get("image_front_url"),
        "in_db": in_db,
    }


def _find_by_name(session, name: str) -> dict | None:
    row = session.execute(
        select(models.Product.id, models.Product.name).where(
            func.lower(models.Product.name) == name.strip().lower()
        )
    ).one_or_none()
    return {"id": row.id, "name": row.name} if row else None


def _tool(name: str, description: str, properties: dict[str, Any]) -> types.Tool:
    return types.Tool(
        name=name,
        description=description,
        input_schema={
            "type": "object",
            "properties": properties,
            "required": [p for p, spec in properties.items() if spec.get("required")],
        },
    )


def _int_arg(args: dict[str, Any], key: str, default: int) -> int:
    value = args.get(key, default)
    if value is None:
        return default
    return int(value)


class _UnknownTool(Exception):
    pass


def _dispatch(name: str, args: dict[str, Any]) -> Any:
    session = SessionLocal()
    try:
        if name == "search_products":
            return search_products(session, args.get("q", ""), _int_arg(args, "limit", 10))
        if name == "get_product":
            return get_product(session, _int_arg(args, "product_id", 0))
        if name == "get_ingredients":
            return get_ingredients(
                session,
                category=args.get("category"),
                limit=_int_arg(args, "limit", 50),
            )
        if name == "get_timer":
            return get_timer(
                session, _int_arg(args, "product_id", 0), _int_arg(args, "temp_c", 21)
            )
        if name == "lookup_barcode":
            return lookup_barcode(str(args.get("barcode", "")))
        raise _UnknownTool(name)
    finally:
        session.close()


def create_server() -> Server:
    async def _list_tools(
        ctx: ServerRequestContext, params: types.PaginatedRequestParams | None
    ) -> types.ListToolsResult:
        return types.ListToolsResult(tools=_TOOLS)

    async def _call_tool(
        ctx: ServerRequestContext, params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        try:
            result = _dispatch(params.name, params.arguments or {})
        except _UnknownTool as exc:
            return _error(f"Herramienta desconocida: {exc}")
        except (ValueError, TypeError) as exc:
            return _error(f"Argumentos inválidos: {exc}")
        except Exception as exc:  # noqa: BLE001
            return _error(str(exc))
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        )

    return Server(
        SERVER_NAME,
        version=SERVER_VERSION,
        on_list_tools=_list_tools,
        on_call_tool=_call_tool,
    )


def _error(message: str) -> types.CallToolResult:
    return types.CallToolResult(
        content=[
            types.TextContent(type="text", text=json.dumps({"error": message}, ensure_ascii=False))
        ],
        is_error=True,
    )


_TOOLS = [
    _tool(
        "search_products",
        "Busca productos fermentados/conservas por nombre o descripción (subcadena, insensible a mayúsculas).",
        {"q": {"type": "string", "required": True}, "limit": {"type": "integer"}},
    ),
    _tool(
        "get_product",
        "Devuelve el detalle completo de un producto (ingredientes, categorías, países, microbios, lácteos y metagenomas).",
        {"product_id": {"type": "integer", "required": True}},
    ),
    _tool(
        "get_ingredients",
        "Lista ingredientes canónicos con el número de productos que los usan; opcional filtrar por categoría.",
        {"category": {"type": "string"}, "limit": {"type": "integer"}},
    ),
    _tool(
        "get_timer",
        "Devuelve el perfil de fermentación de un producto y los días estimados ajustados a la temperatura (modelo Q10).",
        {"product_id": {"type": "integer", "required": True}, "temp_c": {"type": "integer"}},
    ),
    _tool(
        "lookup_barcode",
        "Consulta un código de barras en Open Food Facts y comprueba si el producto existe en nuestra base de datos.",
        {"barcode": {"type": "string", "required": True}},
    ),
]


server = create_server()


async def main() -> None:
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import anyio

    anyio.run(main)
