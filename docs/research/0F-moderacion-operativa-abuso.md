# 0F — Moderación operativa y abuso

- **Tema:** FASE 0 - 0F
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Convertir flag booleano en proceso operativo (cola, estados, bitácora, rol admin). Política para primer usuario externo.

## 1. Estado actual

`app/api/reviews.py`: endpoint `POST /reviews/{review_id}/flag` marca `flagged=True`. Solo eso. Falta cola, estados, resolución, rol admin, bitácora.

## 2. Estados de reporte

`report_status`: `pending | in_review | resolved | dismissed | escalated`

- `pending`: nuevo reporte
- `in_review`: siendo atendido por moderador
- `resolved`: acción tomada (ocultar/bloquear)
- `dismissed`: falso positivo, sin acción
- `escalated`: requiere revisión adicional

## 3. Modelo de datos (propuesto)

Reportes:
- `id`, `reporter_id`, `content_type` (review/recipe/comment/image), `content_id`
- `reason` (enum: spam, abuso, ofensivo, falso, otro)
- `details`, `status`, `moderator_id`, `resolution`, `action_taken` (enum)
- `created_at`, `resolved_at`, `flagged_at_original`
- `ip_hash` (para abuso)

Bitácora inmutable (auditoría):
- `moderation_log`: `id`, `actor_id`, `action`, `target_type`, `target_id`, `metadata` (JSON), `created_at`

## 4. Flujo de moderación

1. Usuario reporta → crea reporte `pending`
2. Moderador toma reporte (`in_review`) — evita doble trabajo
3. Investiga (ver historial usuario, contexto)
4. Resuelve: `resolved` con acción o `dismissed`
5. Aplica sanción si procede (ocultar contenido, suspender usuario temporal)
6. Bitácora inmutable

## 5. Roles

- `user`: puede reportar
- `moderator`: accede cola, resuelve reportes, lee bitácora
- `admin`: gestiona moderadores, ve auditoría completa

## 6. Spam básico y prevención

- Umbral: nuevas cuentas limitadas en publicar/reportar (rate limit)
- Honeypot opcional
- Bloqueo temporal por N reportes válidos
- **No** ML ahora (W1 en comunidad), manual hasta que duela

## 7. Política (anexo ToS)

Elementos mínimos:
- Motivos aceptables, tiempos de respuesta (SLA ligero: 48–72h)
- Transparencia, prevención represalias
- Proceso apelación básico
- Privacidad: no exponer reporte a reportado

## 8. DoD 0F

- [ ] Estados + modelo reportes definido
- [ ] Flujo operativo documentado
- [ ] Bitácora inmutable especificada
- [ ] Roles y permisos
- [ ] Política de moderación (borrador anexo ToS)
- [ ] Spam básico + rate limits
- [ ] Prepara Sprint 6

## Referencias
- Discourse Moderation Guidelines: https://meta.discourse.org/t/moderation-guidelines
- docs/PLAN_SPRINTS.md FASE 0 - 0F, Sprint 6
- docs/DEVIL_ADVOCATE_ANALYSIS.md Razón 3
