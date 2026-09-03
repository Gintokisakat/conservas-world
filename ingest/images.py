"""Asigna imágenes (image_url) a los productos del catálogo.

Fuentes (en orden de prioridad):
1. Open Food Facts: foto real del producto por barcode (productos OFF).
2. Open Food Facts: búsqueda por nombre (fotos de productos comerciales reales).
3. Wikimedia Commons: búsqueda por nombre canónico con validación de licencia.
4. Wikidata: claim de imagen (P18) como último recurso.

Uso:
    python -m ingest.images [--dry-run] [--limit N] [--only-missing]
"""

import argparse
import json
import re
import time
from pathlib import Path

import httpx
from app.db import models
from app.db.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import selectinload

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
OFF_SEARCH_API = "https://world.openfoodfacts.org/api/v2/search"
OFF_PRODUCT_API = "https://world.openfoodfacts.org/api/v2/product"
OFF_LEGACY_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "conservas-world/0.1 (research database seed)"}
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "images"

# Pacer por host: cada API tiene su propio ritmo para no saturarla.
_HOST_PACE = {
    "world.openfoodfacts.org": 1.2,
    "commons.wikimedia.org": 2.0,
    "www.wikidata.org": 1.0,
    "upload.wikimedia.org": 0.0,
}
DEFAULT_PACE = 2.0

# ---------------------------------------------------------------------------
# Utilidades de red y caché (mismo patrón que ingest/sources/wikidata.py)
# ---------------------------------------------------------------------------

_last_request: dict[str, float] = {}

# Marca temporal del último 429: sirve para saltar fuentes no esenciales
# (aliases, Wikidata) mientras el host nos está limitando el ritmo.
# None = nunca hemos recibido un 429 (no usar 0.0: monotonic() arranca en 0
# en procesos recién iniciados y daría throttled() espurios en CI).
_LAST_429: float | None = None


def _throttled() -> bool:
    """True si el último 429 fue hace menos de 90s."""
    return _LAST_429 is not None and time.monotonic() - _LAST_429 < 90.0


def _pace(url: str):
    host = url.split("/")[2]
    pace = _HOST_PACE.get(host, DEFAULT_PACE)
    if pace <= 0:
        return
    last = _last_request.get(host, 0.0)
    elapsed = time.monotonic() - last
    if elapsed < pace:
        time.sleep(pace - elapsed)
    _last_request[host] = time.monotonic()


def _backoff(resp: httpx.Response | None, attempt: int) -> float:
    """Segundos a esperar antes del siguiente intento (respeta Retry-After)."""
    if resp is not None and resp.status_code == 429:
        retry_after = resp.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            return min(float(retry_after), 60.0)
        return float(5 * (attempt + 1))
    return float(5 * (attempt + 1))


def _get(url: str, params: dict, cache_key: str | None = None) -> dict:
    if cache_key:
        path = CACHE_DIR / f"{cache_key}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=60, headers=HEADERS) as client:
        for attempt in range(8):
            _pace(url)
            resp: httpx.Response | None = None
            try:
                resp = client.get(url, params=params)
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                print(
                    f"  [{url.split('/')[2]}] {type(exc).__name__} intento {attempt + 1}, "
                    f"esperando {5 * (attempt + 1)}s ...",
                    flush=True,
                )
                time.sleep(5 * (attempt + 1))
                continue
            if resp.status_code == 200:
                data = resp.json()
                if cache_key:
                    path = CACHE_DIR / f"{cache_key}.json"
                    path.write_text(json.dumps(data), encoding="utf-8")
                return data
            print(
                f"  [{url.split('/')[2]}] {resp.status_code} intento {attempt + 1}, "
                f"esperando {_backoff(resp, attempt):.0f}s ...",
                flush=True,
            )
            if resp.status_code in {429, 500, 502, 503, 504}:
                if resp.status_code == 429:
                    _LAST_429 = time.monotonic()
                time.sleep(_backoff(resp, attempt))
                continue
            resp.raise_for_status()
    raise RuntimeError(f"No se pudo obtener {url} con {params}")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:80] or "x"


# ---------------------------------------------------------------------------
# Validación de licencias (Commons / Wikidata)
# ---------------------------------------------------------------------------

_ALLOWED = re.compile(
    r"^(cc0|cc[ -]by(-sa)?\b|public domain|\bpd\b|apache\b|mit\b|gpl|gfdl|odc)",
    re.I,
)
_BAD = re.compile(
    r"\b(nc\b|nd\b|non-?commercial|no derivatives|fair use|permission\b|"
    r"copyrighted|non-free|all rights reserved|restricted)\b",
    re.I,
)


def license_ok(extmetadata: dict | None) -> bool:
    """True si la imagen tiene licencia libre (sin NC/ND/non-free)."""
    if not extmetadata:
        return False
    names = [
        str(extmetadata.get("LicenseShortName", {}).get("value") or ""),
        str(extmetadata.get("License", {}).get("value") or ""),
        str(extmetadata.get("UsageTerms", {}).get("value") or ""),
    ]
    combined = " ".join(names)
    if _BAD.search(combined):
        return False
    return bool(_ALLOWED.search(combined))


# Términos que indican imágenes genéricas/irrelevantes (logos, mapas, etc.).
_NOISE = re.compile(
    r"\b(logo|map|flag|icon|diagram|chart|portrait|family|people|person|"
    r"building|street|poster|flyer|drawing|illustration|signature|"
    r"coat of arms|seal|stamp|wikimedia|wikipedia|map of|location|"
    r"mausoleum|monument|statue|tomb|temple|church|bridge|museum|"
    r"memorial|plaque|general|senator|politician|president)\b",
    re.I,
)

# Solo fotografías / imágenes rasterizadas (nada de SVG: logos, firmas, mapas).
_RASTER = re.compile(r"\.(jpe?g|png|webp|gif|tiff?|bmp)([?#]|$)", re.I)
_DRAWING = re.compile(r"\b(map|diagram|chart|logo|signature|flag|icon)\b", re.I)


_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "at", "and", "or", "with", "de", "la",
    "el", "los", "las", "del", "en", "con", "para", "por", "et", "au", "aux",
    "le", "les", "un", "une", "das", "der", "die", "und", "mit", "von", "zu",
    "sauerkraut", "pickled", "fermented", "encurtido", "fermentado", "al",
    "style", "estilo", "tipo", "product", "producto", "food", "alimento",
}


def _title_overlaps(name: str, title: str) -> bool:
    """El título de la imagen debe contener al menos un token significativo."""
    tokens = {t for t in re.split(r"[^a-z0-9]+", name.lower()) if len(t) >= 3 and t not in _STOPWORDS}
    if not tokens:
        return True
    title_tokens = set(re.split(r"[^a-z0-9]+", title.lower()))
    return bool(tokens & title_tokens)


def _thumb(pages: list[dict], name: str) -> str | None:
    for page in pages:
        imageinfo = (page.get("imageinfo") or [None])[0]
        if not imageinfo:
            continue
        thumburl = imageinfo.get("thumburl")
        if not thumburl:
            continue
        # Placeholder genérico de Commons para archivos sin thumbnail propio.
        if "file-type-icons" in thumburl or "fileicon-" in thumburl:
            continue
        title = page.get("title") or ""
        if _NOISE.search(title) or _DRAWING.search(title):
            continue
        if not _RASTER.search(thumburl.split("?")[0]):
            continue
        if not _title_overlaps(name, title):
            continue
        if not license_ok(imageinfo.get("extmetadata")):
            continue
        # Quitar parámetros de tracking (utm_*) que añade la API.
        return thumburl.split("?", 1)[0]
    return None


# ---------------------------------------------------------------------------
# Fuente 2: Wikimedia Commons por nombre canónico
# ---------------------------------------------------------------------------


def commons_image(name: str) -> str | None:
    """Busca un thumbnail (400px) con licencia libre en Commons."""
    cache_key = f"commons_{_slug(name)}"
    data = _get(
        COMMONS_API,
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": name,
            "gsrnamespace": "6",
            "gsrlimit": "8",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": "400",
            "format": "json",
            "formatversion": "2",
        },
        cache_key=cache_key,
    )
    pages = data.get("query", {}).get("pages", [])
    return _thumb(pages, name)


# ---------------------------------------------------------------------------
# Fuente 1: Open Food Facts por barcode
# ---------------------------------------------------------------------------


def off_image_by_barcode(code: str) -> str | None:
    """Foto de frente del producto (image_front_url) desde la API de OFF."""
    cache_key = f"off_{code}"
    data = _get(
        f"{OFF_PRODUCT_API}/{code}.json",
        {"fields": "image_front_url,image_front_small_url"},
        cache_key=cache_key,
    )
    product = data.get("product") or {}
    return product.get("image_front_url") or product.get("image_front_small_url")


_OFF_SEARCH_FIELDS = "code,image_front_url,image_front_small_url"


def _fetch_off_search(tag: str, page: int) -> dict:
    cache_key = f"off_search_{tag}.p{page}"
    return _get(
        OFF_SEARCH_API,
        {
            "categories_tags": tag,
            "fields": _OFF_SEARCH_FIELDS,
            "page_size": "50",
            "page": str(page),
        },
        cache_key=cache_key,
    )


def build_off_image_map() -> dict[str, str]:
    """Mapa barcode -> image_front_url a partir del search por categoría (bulk)."""
    from ingest.sources.openfoodfacts import CATEGORIES

    image_map: dict[str, str] = {}
    for tag, cap in CATEGORIES.items():
        page = 1
        total = 0
        while total < cap:
            try:
                data = _fetch_off_search(tag, page)
            except httpx.HTTPStatusError:
                break
            products = data.get("products") or []
            if not products:
                break
            for product in products:
                code = str(product.get("code") or "")
                url = product.get("image_front_url") or product.get("image_front_small_url")
                if code and url:
                    image_map.setdefault(code, url)
            total += len(products)
            if len(products) < 50:
                break
            page += 1
    return image_map


_OFF_BARCODE_RE = re.compile(r"openfoodfacts\.org/product/(\d+)")


def off_barcode(product: models.Product) -> str | None:
    """Extrae el barcode de las referencias OFF del producto."""
    for ref in product.references:
        match = _OFF_BARCODE_RE.search(ref.url or "")
        if match:
            return match.group(1)
    return None


def _fetch_off_by_name(name: str) -> dict:
    """Resultados del search por nombre en OFF (API legacy), con caché por slug.

    La API legacy de OFF puede devolver cuerpo vacío / no-JSON bajo rate-limit;
    por eso se hace el parse defensivo aquí y no se lanza sobre `_get`.
    """
    cache_key = f"off_name_{_slug(name)}"
    path = CACHE_DIR / f"{cache_key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    params: dict[str, str | int] = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "fields": "code,product_name,image_front_url,image_front_small_url",
    }
    payload: dict = {"products": []}
    with httpx.Client(timeout=60, headers=HEADERS) as client:
        for attempt in range(5):
            _pace(OFF_LEGACY_SEARCH)
            try:
                resp = client.get(OFF_LEGACY_SEARCH, params=params)
            except (httpx.ConnectError, httpx.TimeoutException):
                time.sleep(5 * (attempt + 1))
                continue
            if resp.status_code != 200:
                time.sleep(_backoff(resp, attempt))
                continue
            try:
                data = resp.json()
            except ValueError:
                # Cuerpo vacío o no-JSON (rate-limit suave de OFF): reintentar.
                time.sleep(5 * (attempt + 1))
                continue
            payload = data
            break
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def off_name_image(name: str) -> str | None:
    """Foto de frente del producto por búsqueda de nombre en OFF."""
    data = _fetch_off_by_name(name)
    for product in data.get("products") or []:
        url = product.get("image_front_url") or product.get("image_front_small_url")
        if url:
            return url
    return None


# ---------------------------------------------------------------------------
# Fuente 3: Wikidata claim de imagen (P18)
# ---------------------------------------------------------------------------


def _commons_title_to_url(title: str) -> str | None:
    data = _get(
        COMMONS_API,
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": "400",
            "format": "json",
            "formatversion": "2",
        },
        cache_key=f"wikimedia_{_slug(title)}",
    )
    pages = data.get("query", {}).get("pages", [])
    return _thumb(pages, title)


def wikidata_image(product: models.Product) -> str | None:
    """Imagen desde el claim P18 de la entidad Wikidata (último recurso)."""
    for ref in product.references:
        if not ref.url or "wikidata.org/wiki/" not in ref.url:
            continue
        qid = ref.url.rstrip("/").rsplit("/", 1)[-1]
        if not re.fullmatch(r"Q\d+", qid):
            continue
        data = _get(
            WIKIDATA_API,
            {
                "action": "wbgetentities",
                "ids": qid,
                "props": "claims",
                "format": "json",
            },
            cache_key=f"wikidata_{qid}",
        )
        entity = (data.get("entities") or {}).get(qid, {})
        claims = entity.get("claims", {}).get("P18", [])
        for claim in claims:
            try:
                filename = claim["mainsnak"]["datavalue"]["value"]
            except (KeyError, TypeError):
                continue
            return _commons_title_to_url(f"File:{filename}")
    return None


# ---------------------------------------------------------------------------
# Resolución por producto
# ---------------------------------------------------------------------------


def resolve_image(
    product: models.Product,
    off_map: dict[str, str] | None = None,
    skip_off: bool = False,
) -> str | None:
    """Devuelve la mejor imagen disponible para el producto (en orden).

    - Si `skip_off` está activo no se consulta Open Food Facts.
    - Mientras el host esté con rate-limit (429) se evitan las búsquedas de
      aliases y el fallback de Wikidata para no encadenar más peticiones.
    """
    try:
        code = off_barcode(product)
        if code and not skip_off:
            url = off_map.get(code) if off_map else None
            if not url:
                url = off_image_by_barcode(code)
            if url:
                return url

        candidates = [product.name]
        for alias in product.aliases:
            if alias.language in ("en", "orig", None):
                candidates.append(alias.name)
        seen = set()
        for name in candidates:
            key = name.lower().strip()
            if not key or key in seen:
                continue
            seen.add(key)
            # Fuente 1b: Open Food Facts por nombre (foto real de producto).
            if not skip_off and not _throttled():
                url = off_name_image(name)
                if url:
                    return url
            url = commons_image(name)
            if url:
                return url
            if _throttled():
                return None
            if not _throttled():
                return wikidata_image(product)
            return None
        return None
    except RuntimeError:
        # El host se negó de forma persistente (rate-limit agotado): sin imagen,
        # pero no tiramos el pipeline.
        return None


def main():
    parser = argparse.ArgumentParser(description="Asigna imágenes a los productos")
    parser.add_argument("--dry-run", action="store_true", help="No escribe cambios")
    parser.add_argument("--limit", type=int, default=0, help="Limitar a N productos (0 = todos)")
    parser.add_argument(
        "--only-missing", action="store_true", help="Solo productos sin image_url"
    )
    parser.add_argument(
        "--skip-off", action="store_true", help="No consultar Open Food Facts"
    )
    parser.add_argument(
        "--skip-off-map",
        action="store_true",
        help="Omitir el mapa masivo de barcodes OFF (más rápido, mantiene consultas OFF por producto)",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        products = session.execute(
            select(models.Product)
            .options(selectinload(models.Product.references), selectinload(models.Product.aliases))
            .where(models.Product.status != "discarded")
            .order_by(models.Product.id)
        ).scalars().all()
        if args.limit:
            products = products[: args.limit]
        if args.only_missing:
            products = [p for p in products if not p.image_url]

        off_map = None if args.skip_off_map else ({} if args.skip_off else build_off_image_map())

        # Los productos con barcode OFF se resuelven por API directa (rápido);
        # procesarlos primero reduce el tiempo total de espera.
        products = sorted(
            products, key=lambda p: (off_barcode(p) is None)
        )

        done = 0
        failed = 0
        for index, product in enumerate(products, start=1):
            if product.image_url and not args.only_missing:
                continue
            url = resolve_image(product, off_map=off_map, skip_off=args.skip_off)
            if url:
                if not args.dry_run:
                    product.image_url = url
                done += 1
                print(f"  [{product.id}] {product.name!r} -> {url}", flush=True)
            else:
                failed += 1
            # Commit tras cada asignación y de forma incremental: no perder
            # el progreso si el proceso se interrumpe o OFF nos limita el ritmo.
            if not args.dry_run and (url or index % 20 == 0):
                session.commit()
        if not args.dry_run:
            session.commit()
    finally:
        session.close()

    print(f"\nImágenes asignadas: {done}")
    print(f"Sin imagen encontrada: {failed}")


if __name__ == "__main__":
    main()
