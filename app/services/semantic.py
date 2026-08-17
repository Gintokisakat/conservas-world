"""Búsqueda semántica ligera (3.5) basada en similitud coseno TF-IDF.

Alternativa sin dependencias pesadas (sin sentence-transformers ni FAISS):
se construye un índice TF-IDF en memoria sobre nombre + descripción + método
+ ingredientes de todos los productos activos, y se rankea por coseno.

El índice se construye perezosamente y se cachea, invalidándose si cambia
el número de productos o la fecha de última actualización.
"""

import math
import re

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import models

_TOKEN_RE = re.compile(r"[a-záéíóúüñç0-9]+")
_STOPWORDS = {
    "a", "al", "con", "de", "del", "el", "en", "es", "la", "las", "los", "para",
    "por", "que", "se", "su", "un", "una", "y", "o", "e", "the", "of", "and",
    "to", "in", "with", "for", "from", "on", "is", "are", "it", "its", "como",
    "tipo", "tradicional", "tradición", "elaborado", "elaboración", "producto",
    "food", "product", "traditional", "made", "using", "used", "also", "well",
}


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS and len(t) > 1]


def _dataset_fingerprint(session: Session) -> tuple[int, str]:
    from sqlalchemy import func

    count = session.execute(
        select(func.count()).select_from(models.Product).where(
            models.Product.status.in_(["imported", "reviewed"])
        )
    ).scalar_one()
    latest = session.execute(
        select(func.max(models.Product.updated_at)).where(
            models.Product.status.in_(["imported", "reviewed"])
        )
    ).scalar_one()
    return (count, str(latest or ""))


class _Index:
    __slots__ = ("df", "idf", "doc_norms", "product_ids", "terms")

    def __init__(self) -> None:
        self.df: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.doc_norms: list[float] = []
        self.product_ids: list[int] = []
        self.terms: list[list[tuple[str, float]]] = []


_index: _Index | None = None
_index_fingerprint: tuple[int, str] | None = None


def _build_index(session: Session) -> _Index:
    global _index, _index_fingerprint

    fingerprint = _dataset_fingerprint(session)
    if _index is not None and _index_fingerprint == fingerprint:
        return _index

    products = session.execute(
        select(models.Product)
        .options(selectinload(models.Product.ingredients))
        .where(models.Product.status.in_(["imported", "reviewed"]))
    ).scalars().all()

    index = _Index()
    token_docs: dict[str, set[int]] = {}

    for doc_id, p in enumerate(products):
        text = " ".join(
            [p.name, p.description or "", p.method or "",
             " ".join(i.name for i in p.ingredients)]
        )
        toks = tokenize(text)
        tf: dict[str, int] = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        for t in tf:
            token_docs.setdefault(t, set()).add(doc_id)
        terms = [(t, float(freq)) for t, freq in tf.items()]
        norm = math.sqrt(sum((1 + math.log(f)) ** 2 for _, f in terms)) or 1.0
        index.terms.append(terms)
        index.doc_norms.append(norm)
        index.product_ids.append(p.id)

    index.df = {t: len(docs) for t, docs in token_docs.items()}
    n_docs = len(products)
    index.idf = {t: math.log((1 + n_docs) / (1 + df)) + 1 for t, df in index.df.items()}

    _index = index
    _index_fingerprint = fingerprint
    return index


def semantic_search(session: Session, query: str, limit: int = 20) -> list[dict]:
    index = _build_index(session)
    q_tokens = tokenize(query)
    if not q_tokens or not index.product_ids:
        return []

    q_tf: dict[str, int] = {}
    for t in q_tokens:
        q_tf[t] = q_tf.get(t, 0) + 1
    q_weights = {t: (1 + math.log(f)) * index.idf.get(t, 0.0) for t, f in q_tf.items()}
    if not q_weights:
        return []
    q_norm = math.sqrt(sum(w * w for w in q_weights.values())) or 1.0

    scores: list[tuple[float, int]] = []
    for doc_id, terms in enumerate(index.terms):
        acc = 0.0
        for t, freq in terms:
            w = q_weights.get(t)
            if w:
                acc += (1 + math.log(freq)) * index.idf[t] * w
        if acc > 0:
            scores.append((acc / (index.doc_norms[doc_id] * q_norm), index.product_ids[doc_id]))

    scores.sort(reverse=True)
    ranked_ids = [pid for _, pid in scores[:limit]]
    if not ranked_ids:
        return []

    products = session.execute(
        select(models.Product).where(models.Product.id.in_(ranked_ids))
    ).scalars().all()
    by_id = {p.id: p for p in products}
    return [
        {
            "product_id": pid,
            "score": round(score, 4),
            "name": by_id[pid].name,
            "description": by_id[pid].description,
            "image_url": by_id[pid].image_url,
            "source_tag": by_id[pid].source_tag,
        }
        for score, pid in scores[:limit]
        if pid in by_id
    ]