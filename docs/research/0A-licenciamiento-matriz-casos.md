# 0A complementario: matriz de casos y compatibilidad ODbL

Complementa ADR-0001 con casos prácticos (FTS/embeddings/mapeo/export/API).

## Matriz de casos

| Caso | ¿Derivado? | ¿Afecta BD? | Acción |
|---|---|---|---|
| Indexado FTS/tsvector | Depende interpretación | Indexar no copia texto completo | Marcar trazabilidad; respetar license |
| Embeddings | Probable derivado | Sí | No usar datos NC para embeddings comerciales |
| Mapeo por nombre (normalización) | Alto riesgo NC-ND | Potencial derivado | Evitar con NC-ND |
| Export CSV/JSON | Distribución | Cuidado ODbL SA | Atribuir + respetar SA |
| API pública | Distribución efectiva | Evaluar | Limitar a datos commercial-ready |
| SSR /p/{id} | Exposición | Evaluar | Respetar atribución |

## Compatibilidad ODbL

Mezclar ODbL con CC SA: complejo. Mezclar con datos internos PROPRIETARY: requiere análisis. 
NC-SA/NC-ND: incompatibles con uso comercial.

Ver scripts/check_license_compat.py + gate license-check.
