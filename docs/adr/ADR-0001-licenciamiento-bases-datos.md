# ADR-0001: Licenciamiento de bases de datos (ODbL vs CC) y política de mezcla para uso comercial

- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Autor:** Decisión técnica (FASE 0 - 0A)
- **Relacionado:** ROADMAP.md, docs/PLAN_SPRINTS.md, docs/DEVIL_ADVOCATE_ANALYSIS.md

## Contexto

El objetivo pasa a ser comunidad + comercial. Hay que decidir qué fuentes de datos son admisibles para un producto comercial, cómo tratamos la mezcla entre ellas y cómo garantizar trazabilidad para evitar violar licencias (especialmente NC-ND/NC-SA y ODbL).

Fuentes relevantes identificadas en el proyecto:
- Open Food Facts: ODbL 1.0
- FooDI-ML: CC BY-NC-SA (mencionado en roadmap como 2.4 relacionado)
- Flavor Network: CC BY-NC-SA
- FermFooDb (péptidos bioactivos, 2.4): CC BY-NC-ND — prohibitivo para comercial
- Otras fuentes curadas internas (propias): sin licencia heredada, pueden ser propietarias o CC0

## Pregunta a resolver (0A)

1. ¿Cuándo es una obra derivada vs una base de datos derivada bajo ODbL 1.0 (Arts. 2 y 4)?
2. En CC BY-NC-ND, ¿qué cuenta como «adaptación»/derivado al indexar, extraer, mapear por nombre, normalizar o incluir en un índice de búsqueda (FTS/tsvector) o embeddings?
3. Compatibilidad entre licencias con share-alike (ODbL SA, CC BY-SA/NC-SA) ante mezcla de datasets.
4. ¿Podemos mantener una base privada/comercial mezclando datos? ¿Qué obliga ODbL sobre bases derivadas?
5. Estrategia de trazabilidad por fila (source, license, commercial_use_allowed, derivatives_allowed, share_alike).

## Decisión preliminar (por investigar y validar)

Principio: **separación por procedencia y firewall de licenciamiento**. No mezclamos indiscriminadamente.

### Recomendación de política

1. **Trazabilidad obligatoria por fila**: todo registro importado debe tener:
   - `source` (slug), `source_id`, `source_url`
   - `source_license` (SPDX o cadena canónica: `ODbL-1.0`, `CC-BY-NC-SA-4.0`, `CC-BY-NC-ND-4.0`, `CC-BY-4.0`, `CC0-1.0`, `PROPRIETARY`, `INTERNAL`)
   - `source_attribution` (texto obligatorio si requiere atribución)
   - `commercial_use_allowed` (bool), `derivatives_allowed` (bool), `share_alike` (bool)
   - `is_commercial_ready` (bool calculado desde origen)

2. **Aislamiento NC-ND (FermFooDb)**: CC BY-NC-ND prohíbe crear obras derivadas y uso no comercial. Cualquier mapeo por nombre, normalización o inclusión en índices constituye derivado. **Conclusión preliminar:** excluirlo completamente del pipeline para uso comercial. Mantenerlo aislado con `ENABLE_NC_DATA=false` por defecto.

3. **NC-SA (FooDI-ML, Flavor Network)**: uso no comercial prohibido para producto comercial. Share-alike obliga a relicenciar bajo misma licencia si distribuimos obra derivada. Para base de datos derivada bajo ODbL el tratamiento difiere. **Conclusión preliminar:** no admisible para vía comercial directa.

4. **ODbL 1.0 (Open Food Facts)**: obliga a mantener licencia ODbL en la base de datos derivada y a ofrecer acceso a la misma bajo ODbL (copyleft de BD). Esto complica un modelo 100% propietario. **Necesario aclarar**: ¿nuestros índices/servicio son «producción de una obra derivada» o «uso»? Distinción BD vs contenido.

5. **Firewall en ingesta**: gate `COMMERCIAL_READY` rechaza filas con `commercial_use_allowed=false` si mezcladas. Ver `P0-6` (license firewall).

## Acciones para cerrar 0A (DoD)

- [ ] Recopilar citas textuales (ODbL Arts. 2, 4, 6; CC licenses §1/§3) sobre derivado/indexado
- [ ] Matriz de casos: búsqueda (FTS), embeddings, mapeo por nombre, normalización, export CSV/JSON, API pública, SSR
- [ ] Matriz de compatibilidad ODbL + CC ante mezcla
- [ ] ADR definitivo con conclusión por cada fuente
- [ ] Crear `data/licenses/` con textos y notas

## Estado actual
**Draft** — requiere investigación jurídica/técnica antes de tomar decisión definitiva. No bloquear por completo, pero sí antes de Sprint 0.

## Referencias
- ODbL 1.0: https://opendatacommons.org/licenses/odbl/1-0/
- CC Legal: https://creativecommons.org/licenses/
- Open Knowledge: https://opendefinition.org/
- docs/DEVIL_ADVOCATE_ANALYSIS.md (Razón 2)
- docs/PLAN_SPRINTS.md FASE 0 - 0A
