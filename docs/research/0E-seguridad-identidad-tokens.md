# 0E — Seguridad de identidad (tokens)

- **Tema:** FASE 0 - 0E
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Definir estrategia segura (refresh rotation + reuse detection, jti/blocklist, verificación email con one-time token). Decidir Redis vs BD para revocación.

## 1. Estado actual

`app/services/auth.py` implementa JWT + refresh tokens. Según análisis: falta verificación de email, reset de contraseña, revocación robusta de sesiones y rate limiting compartido entre réplicas.

## 2. Principios (basado OWASP + RFC 6819)

- **Refresh token rotation**: cada uso de refresh genera nuevo refresh token; antiguo se invalida
- **Reuse detection**: si refresh token reutilizado (ya revocado/usado) → invalidar toda familia de tokens (posible compromiso)
- **jti (JWT ID)** para revocación individual
- **Blocklist** para access tokens cortos (opcional) o preferir lifetimes cortos
- **Verificación email con one-time token (no JWT)**: token aleatorio almacenado con hash + expiración, de un solo uso
- **Reset contraseña con one-time token**: similar, independiente de sesión

## 3. Estrategia de tokens

| Tipo | Formato | Lifetime | Uso | Almacenamiento |
|---|---|---|---|---|
| Access | JWT corto | corto (15m recomendado) | API | Cliente (memoria) |
| Refresh | Token opaco (aleatorio) o JWT con jti | largo (7–30d) | Renovar access | HttpOnly Secure SameSite |
| Email verify | Token aleatorio (bytes → base64url) | 24h | Verificar email | Hash en BD (exp + usado) |
| Password reset | Token aleatorio | 1h | Reset | Hash en BD (exp + usado + user_id) |

**Recomendación:** refresh opaco (más fácil de revocar) vs JWT. Verificación/reset SIEMPRE opacos con hash.

## 4. Revocación (blocklist)

Necesario para refresh revocados y detección reuse. Hoy en memoria no sobrevive despliegues/múltiples réplicas (P0-13).

Opciones:
- **Redis (recomendado):** TTL automático, compartido entre réplicas, rápido. Necesario para producción con réplicas
- **BD:** lista `revoked_tokens` (jti, expires_at) — persistente pero requiere limpieza periódica

**Decisión:** Redis para blocklist de refresh + detección reuse (P0-13). Mantenemos BD para tokens one-time (verify/reset) por atomicidad.

## 5. Flujo refresh rotation + reuse detection

1. Cliente envía refresh token válido
2. Buscar familia (token_id/family_id). Si ya revocado → marcar familia comprometida → revocar todos refresh de usuario → 401
3. Generar nuevo refresh + access, revocar antiguo (rotation)
4. Si se recibe refresh ya usado → reuse detected → revocar familia → 401 (sospecha compromiso)

## 6. Rate limiting

Por IP + por cuenta (login/register/verify/reset). Debe ser compartido entre réplicas → Redis.

## 7. Checklist de amenazas (OWASP)

- [ ] Brute force: rate limit login
- [ ] Token theft: rotation + reuse detection
- [ ] CSRF: SameSite=Lax/Strict para refresh cookies
- [ ] XSS: HttpOnly Secure
- [ ] Token leakage: no logear tokens
- [ ] Timing attacks: comparar hashes constantes

## 8. DoD 0E

- [ ] Especificación rotation + reuse detection
- [ ] Decisión Redis vs BD documentada (Redis blocklist)
- [ ] Especificación one-time tokens (verify/reset) con hash
- [ ] Checklist amenazas completo
- [ ] Lifetimes definidos
- [ ] Prepara Sprint 4 y P0-13

## Referencias
- OWASP Auth Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- RFC 6819: https://datatracker.ietf.org/doc/html/rfc6819
- RFC 6749: https://datatracker.ietf.org/doc/html/rfc6749
- docs/PLAN_SPRINTS.md FASE 0 - 0E, Sprint 4
- docs/DEVIL_ADVOCATE_TASKS.md P0-13
