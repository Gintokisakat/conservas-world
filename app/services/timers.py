"""Perfiles de fermentación y estimación de tiempos por temperatura.

Modelo Q10 simplificado: cada +10 °C duplica la velocidad de fermentación
respecto a la temperatura de referencia de 21 °C. El texto de fermentación
(``fermentation_time``) se parsea en un rango de días base.
"""

import re
import unicodedata

# Patrones para parsear tiempos de fermentación en días.
_TIME_PATTERNS = [
    (re.compile(r"(\d+)\s*[-–]\s*(\d+)\s*(d[íi]as?|dias?|semanas?|meses?|a[ñn]os?)", re.I), 1),
    (re.compile(r"(\d+)\s*(d[íi]as?|dias?|semanas?|meses?|a[ñn]os?)", re.I), 2),
]
_UNIT_DAYS = {
    "dia": 1, "dias": 1,
    "semana": 7, "semanas": 7,
    "mes": 30, "meses": 30,
    "ano": 365, "anos": 365,
}

REFERENCE_TEMP_C = 21.0


def _norm_unit(unit: str) -> str:
    unit = unit.lower()
    return "".join(c for c in unicodedata.normalize("NFD", unit) if unicodedata.category(c) != "Mn")


def parse_days(text: str | None) -> tuple[int, int] | None:
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


def estimate_days(text: str | None, temp_c: float = REFERENCE_TEMP_C) -> dict:
    """Días estimados ajustados a una temperatura (modelo Q10).

    Devuelve ``{"min": ..., "max": ...}`` en días o ``None`` si el texto no
    declara un rango parseable.
    """
    base = parse_days(text)
    if base is None:
        return {"min": None, "max": None}
    factor = 2 ** ((REFERENCE_TEMP_C - temp_c) / 10)
    lo, hi = base
    return {"min": round(lo * factor), "max": round(hi * factor)}