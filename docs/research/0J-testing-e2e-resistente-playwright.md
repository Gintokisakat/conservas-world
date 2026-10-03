# 0J — Testing E2E resistente (Playwright)

- **Tema:** FASE 0 - 0J
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Guía para tests E2E resistentes (evitar sleeps, fixtures aislados, accesibles). Prepara M6/N6/Sprint 7.

## 1. Principios

- **Aislamiento por test:** DB seed limpio, no compartir estado
- **Evitar sleeps:** usar `waitFor`, `expect` con auto-retry
- **Accesibles:** preferir getByRole/getByLabel/getByText
- **Deterministas:** evitar timeouts aleatorios, datos fijos
- **Screenshots en fallo:** diagnóstico rápido

## 2. Fixtures

- Auth fixture reutilizable (login vía API o UI)
- DB seed por test (rollback o transacción/truncate)
- Setup/teardown aislado

## 3. Estrategias anti-flakiness

- Usar web-first assertions (`expect.toBeVisible`)
- Esperar red (`waitForResponse`, `waitForLoadState`)
- Retries configurados por CI
- No depender de animaciones

## 4. Cobertura mínima

Flujos críticos:
1. Crear lote → checkpoint → marcar listo (M6)
2. Buscar → detalle → publicar reseña → moderarla (N6/Sprint 7)

## 5. DoD 0J

- [ ] Guía escrita (fixtures, aislamiento, anti-flakiness)
- [ ] Config Playwright propuesta
- [ ] Estrategia DB seed aislado
- [ ] 2 flujos mínimos definidos
- [ ] Prepara Sprint 7

## Referencias
- Playwright Best Practices: https://playwright.dev/docs/best-practices
- docs/PLAN_SPRINTS.md FASE 0 - 0J, M6/N6/Sprint 7
