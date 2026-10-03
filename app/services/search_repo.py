"""Adaptador de búsqueda (FASE 0C/P0-4)."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import config


def _sanitize_fts_tokens(term: str) -> list[str]:
    tokens = [t for t in term.split() if t]
    safe: list[str] = []
    for t in tokens:
        cleaned = re.sub(r'[^\w\s-]', '', t, flags=re.UNICODE)
        cleaned = cleaned.strip()
        if cleaned:
            safe.append(cleaned)
    return safe


class SearchRepo(ABC):
    @abstractmethod
    def matches(self, session: Session, term: str, limit: int = 1000) -> list[int] | None:
        ...


class SqliteFtsRepo(SearchRepo):
    def matches(self, session: Session, term: str, limit: int = 1000) -> list[int] | None:
        safe_tokens = _sanitize_fts_tokens(term)
        if not safe_tokens:
            return []
        match = " AND ".join(f'"{t}"*' for t in safe_tokens)
        try:
            rows: Sequence[int] = (
                session.execute(
                    text(
                        "SELECT rowid FROM products_fts "
                        "WHERE products_fts MATCH :t ORDER BY bm25(products_fts) LIMIT :limit"
                    ),
                    {"t": match, "limit": limit},
                )
                .scalars()
                .all()
            )
            return list(rows)
        except Exception:
            return None


class LikeRepo(SearchRepo):
    def matches(self, session: Session, term: str, limit: int = 1000) -> list[int] | None:
        safe_tokens = _sanitize_fts_tokens(term)
        if not safe_tokens:
            return []
        clauses = []
        params: dict[str, str] = {}
        for i, t in enumerate(safe_tokens):
            clauses.append(f"lower(p.name) LIKE :t{i}")
            params[f"t{i}"] = f"%{t.lower()}%"
        q = text(
            "SELECT p.id FROM products p "
            "WHERE " + " AND ".join(clauses) + " ORDER BY p.id LIMIT :limit"
        )
        try:
            rows: Sequence[int] = (
                session.execute(q, {**params, "limit": limit}).scalars().all()
            )
            return list(rows)
        except Exception:
            return None




def get_search_repo() -> SearchRepo:
    backend = config.SEARCH_BACKEND
    if backend == "pg":
        return PgTsvectorRepo()
    if backend == "like":
        return LikeRepo()
    return SqliteFtsRepo()


class PgTsvectorRepo(SearchRepo):
    def matches(self, session: Session, term: str, limit: int = 1000) -> list[int] | None:
        safe_tokens = _sanitize_fts_tokens(term)
        if not safe_tokens:
            return []
        # Usar websearch_to_tsquery para comportamiento natural
        qtext = " ".join(safe_tokens)
        try:
            sql = text(
                """
                SELECT id
                FROM products
                WHERE to_tsvector('simple', coalesce(name,'')) @@ websearch_to_tsquery('simple', :q)
                ORDER BY ts_rank(to_tsvector('simple', coalesce(name,'')), websearch_to_tsquery('simple', :q)) DESC
                LIMIT :limit
                """
            )
            rows: Sequence[int] = (
                session.execute(sql, {"q": qtext, "limit": limit}).scalars().all()
            )
            return list(rows)
        except Exception:
            return None
