# Risk Log

Basado en análisis del abogado del diablo (docs/DEVIL_ADVOCATE_ANALYSIS.md).

| ID | Riesgo | Prob | Impacto | Mitigación | Dueño | Estado | Revisar |
|---|---|---|---|---|---|---|---|
| R1 | PostgreSQL+FTS5 en misma oleada | Alta | Muy alto | Feature flags + adaptador SearchRepo + dual-read + umbral relevancia (P0-1–P0-4) | backend | Mitigado-parcial | Cada sprint |
| R2 | Licencias NC (NC-ND/NC-SA) + ODbL | Media-Alta | Muy alto | Trazabilidad por fila + license firewall + aislamiento ENABLE_NC_DATA + gate CI (P0-5–P0-8) | legal+backend | En seguimiento | Sprint 0 |
| R3 | Pérdida localStorage (ventana irreversible) | Alta | Muy alto | Lectura dual + merge conflictos + dry-run+backup + pre-check (P0-9–P0-12) | frontend+backend | Pendiente aplicar | 9a antes Sprint 3 |
| R4 | Redis/rate limits no compartidos entre réplicas | Media | Alto | Redis blocklist + rate limits (P0-13) | backend | Pendiente | Sprint 4/8 |
| R5 | Moderación + identidad antes primer usuario externo | Alta | Alto | Sprint 4–6 + política (0F,0E) | backend | Planificado | Antes externo |
