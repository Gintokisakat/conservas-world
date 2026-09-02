# Revisión de fuentes curadas (semi-manuales)

CSVs generados por `build_csvs.py` a partir de literatura académica verificada.
**Tu tarea**: abrir cada CSV, corregir lo que quieras y marcar la columna `include`:

- `yes` → se ingiere tal cual
- `no` → se ignora
- `check` → fila ambigua que necesita tu decisión (p. ej. nombres pegados en una celda)

| Archivo | Filas | Fuente |
|---|---|---|
| `africa_east.csv` | 63 | Food Sci Nutr 2025 (PMC11877266), tablas 1-2 |
| `africa_west.csv` | 13 | Microorganisms 2022 (PMC8857253), tabla 1 |
| `mena_dairy.csv` | 18 | Int Dairy J 2023, review MENA |
| `central_asia.csv` | 12 | Int Dairy J 2021/2022, reviews de Asia Central |
| `oceania.csv` | 11 | Pollock 1984 / Atchley & Cox 1985 / Aalbersberg 1988 |
| `latam.csv` | 11 | Foods 2022 review Ecuador + clásicos andinos |
| `caribbean.csv` | 34 | Fermentos y conservas de LatAm + Caribe (Foods 2022, Colegio de Postgraduados, Tamang & Samuel, ICBF) |
| `east_southeast_asia.csv` | 34 | Fermentos del este y sudeste asiático + NE India (Foods 2021 review, Thai cuisine, Katsuyama) |
| `mexico_quesos.csv` | 38 | Atlas Quesos Artesanales Mexicanos (Colegio de Postgraduados) |

## Columnas

- `name`: nombre del producto (tal como aparecerá)
- `country`: país/región (texto libre; la ingesta resuelve con pycountry+aliases)
- `substrate`: materia prima
- `category`: categoría interna propuesta (`fermento_lactico`, `encurtido_fermentado`,
  `fermento_alcoholico`, `fermento_alcalino`, `otro`…)
- `description_es`, `microbiota`, `source_ref`: metadatos opcionales

## Regenerar

```bash
uv run python review/build_csvs.py
```

Las descargas de PMC quedan cacheadas en `_cache/`; si un día el challenge
bloquea httpx: `curl -sL -A 'Mozilla/5.0' <url> -o review/_cache/<nombre>`.
