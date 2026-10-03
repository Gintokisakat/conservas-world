## 4. Ajustes concretos al roadmap (propuesta de inserción)

Modificar `docs/PLAN_SPRINTS.md` con este orden:

1. **Insertar FASE 0 — Aprendizaje** (5–6 h/semana durante 3–4 semanas) **antes** de Sprint 0. No escribe features, escribe decisiones.
2. **Insertar FASE 0b — Blindaje preventivo (P0-1..P0-16)** como **Sprint -1 / Pre-sprints**: dividir en 2 sprints cortos (11+11 h) centrados en feature flags, adaptador de búsqueda, license firewall, coexistencia y dry-run. Esto rompe el triple acoplamiento (legal+datos+búsqueda).
3. **Dividir Sprint 9** en **9a (coexistencia + dry-run + merge)** y **9b (consolidación tras migración)**. 9a debe ejecutarse **antes** de Sprint 3 (migración Postgres), para no crear la ventana irreversible.
4. **Añadir gates de calidad obligatorios**: `license-check`, `search-relevance-threshold`, `migration-dry-run` en CI como jobs bloqueantes.
5. **Actualizar DoD global** para incluir: «sin flags temporales sin fecha de caducidad» y «rollback probado».

## 5. Veredicto del abogado del diablo

El plan es sólido en diagnóstico y honesto en alcance. Los tres puntos de fallo son **exactos** y comparten un denominador común: **tres migraciones críticas en secuencia sin aislamiento** (licencias, motor de búsqueda, datos del usuario). Con los P0 anteriores se reduce drásticamente la probabilidad, pero **no se elimina**.

**Recomendación inequívoca:** **no empieces por el código. Empieza por Fase 0 (0A–0J)**. Ese gasto de 15–20 h de investigación ahorra 6–12 semanas de firefighting con seguridad. Especialmente 0A (licenciamiento) y 0B (FTS→tsvector) son los que, si no se resuelven por escrito primero, invalidan cualquier estimación posterior.