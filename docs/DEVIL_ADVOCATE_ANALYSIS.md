# Acta del abogado del diablo
Responsable: análisis crítico. Bases: `ROADMAP.md`, `docs/PLAN_SPRINTS.md`, `docs/PLAN_LANZAMIENTO.md`, `render.yaml`, `app/api/routes.py`, `app/static/app.js`, `app/static/sw.js`, `app/services/auth.py`.

## 1. 3 razones exactas por las que va a fracasar o retrasarse masivamente

### Razón 1: Encararse a PostgreSQL + FTS5 en una sola oleada (N1–N2)

**Punto exacto de fallo:** El plan pone como Must el cambio de SQLite a PostgreSQL gestionado y la reescritura simultánea de la búsqueda (`products_fts` con `bm25()` en `app/api/routes.py:101`) a `tsvector` + GIN. Se estima 20–40 h.

**Por qué falla:**
- **Acoplamiento de SQL a SQLite:** las consultas usan `MATCH ?` + `bm25(products_fts, ?)` y funciones específicas de FTS5. El fallback `LIKE` existe, pero el ranking y los tests que dependen de ese orden no están cubiertos. Cambiar dos cosas críticas al mismo tiempo hace inmanejable el rollback.
- **Riesgo de regresión de relevancia:** «probar relevancia a mano» (Sprint 2) no es reproducible. Sin un conjunto de queries canónico y un umbral de aceptación (top-k idéntico o NDCG), se aprobará con sesgo. Eso rompe la búsqueda que hoy funciona para 4.259 productos.
- **Operación en producción:** migrar 4.259 filas + índices FTS a tsvector requiere conversión y reindexado con la app en marcha. Sin feature flag de búsqueda (`search_backend: sqlite|pg|like`) no hay forma segura de conmutar.

**Retraso estimado si falla:** +4–8 semanas (doble de N2). Probabilidad alta.

### Razón 2: Legalidad y datos con licencia NC (Sprint 0 pospuesto en la práctica)

**Punto exacto de fallo:** El plan tiene Sprint 0 como bloqueante, pero el propio texto deja abiertas la estrategia de «procedencia por campo». En la práctica, separar texto *verbatim* vs hecho curado es difícil de imponer en el código.

**Por qué falla:**
- **CC BY-NC-ND es prohibitivo:** `2.4 Péptidos bioactivos` (FermFooDb) con NC-ND hace que cualquier mapeo por nombre sea una obra derivada. Esto no se resuelve con atribución: es una prohibición de uso comercial. No basta con «excluirlo del pipeline comercial»: hay que garantizar que ni los índices, ni embeddings, ni descripciones lo referencien o lo mezclen.
- **ODbL tiene share-alike sobre la base derivada:** si se mezclan filas ODbL con datos propios y se publica la BD completa, ODbL obliga a ponerla a disposición bajo ODbL. Si el modelo de negocio pretende una base privada, esto es incompatible con la mezcla indiscriminada. Hoy no hay trazabilidad de origen por fila (`source_license`, `source_id`, `is_derivable_commercial`).
- **Coste oculto de reingeniería:** descubrirlo después de migrar a Postgres o después de añadir comunidad significa reescribir ingestas, volver a indexar y probablemente purgar datos. Ese trabajo no aparece en N1 (6–8 h) sino que escala con el volumen mezclado.

**Retraso estimado si falla:** 6–12 semanas (paraliza comercialización y puede forzar un fork de datos). Probabilidad media-alta.

### Razón 3: Identidad + Moderación + Datos del navegador = ventana irreversible (Sprints 4–6 y 9)

**Punto exacto de fallo:** `pantry_timers`, `pantry_prod`, `pantry_favs` viven en `localStorage` (múltiples usos en `app/static/app.js`). El importador a `/me/batches` está en Sprint 9, pero los flujos de identidad real (verificación/reset/export/borrado) son Sprints 4–6 y la migración a Postgres en 1–3.

**Por qué falla:**
- **Ventana de pérdida irreversible:** si se migra la BD a Postgres antes de ejecutar el importador con todos los casos reales, los lotes del usuario en su navegador se pierden. El plan dice «exportar `localStorage` a un archivo antes de migrar» (30 min), pero eso depende de que el desarrollador recuerde ese paso exacto en el momento preciso. No hay un guardián en CI ni una comprobación de pre-migración.
- **No hay estrategia de coexistencia:** no existe un periodo de lectura dual (localStorage + servidor) ni un *merge* con resolución de conflictos. El usuario puede tener lotes distintos en dos pestañas/navegadores antes de iniciar sesión. El plan no especifica cómo se resuelven duplicados (por `updated_at`, por ID cliente, etc.).
- **Coste de soporte invisible:** identidad, moderación y GDPR son trabajo no visible (0 UI que venda). Con 5,6 h/semana es fácil aplazarlos «un sprint más» y, cuando hay el primer usuario externo, se convierte en firefighting diario que bloquea todo lo demás. Además, `SECRET_KEY`/refresh revocación y rate limits en memoria hoy no sobreviven a despliegues (Redis necesario si hay múltiples réplicas).

**Retraso estimado si falla:** +4–6 semanas, con riesgo reputacional alto. Probabilidad alta.

**Conclusión:** El mayor riesgo no es técnico, es **secuencial y de sincronización entre decisiones legales + datos del usuario + migración de backend**. Tres cambios que se tocan entre sí y ninguno tiene una bandera de rollback independiente.