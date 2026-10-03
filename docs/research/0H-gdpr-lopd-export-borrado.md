# 0H — Derecho de datos (GDPR/LOPD): export y borrado de cuenta

- **Tema:** FASE 0 - 0H
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Cumplir derechos acceso, rectificación, supresión, portabilidad. Sprint 5.

## 1. Ámbito

Derechos ARSOP (Acceso, Rectificación, Supresión, Oposición, Portabilidad). Enfoque: export completo y borrado con cascada verificable.

## 2. Datos por entidad (matriz preliminar)

| Entidad | Datos | Sensible | Retención | Acción al borrar usuario |
|---|---|---|---|---|
| users | email, hash, timestamps | email | mientras cuenta activa | marcar eliminado o borrar según política |
| refresh_tokens | tokens | sí | hasta caducidad/revocado | borrar |
| batches | lotes/temporizadores | no | hasta borrado cuenta | borrar (o anonimizar) |
| reviews | reseñas | no | hasta borrado cuenta | borrar o anonimizar (contenido público) |
| recipes | recetas | no | hasta borrado cuenta | borrar o anonimizar |
| images | fotos | no | hasta borrado cuenta | borrar archivos + DB |
| reportes | moderation | no (admin) | auditoría | conservar **anónimos** para prevenir abuso |
| moderation_log | bitácora | no | obligatoria auditoría | conservar anónimo (inmutable) |
| api_keys | claves | sí | hasta revocación | borrar |

**Principio:** bitácora de moderación debe permanecer **inmutable y anónima** tras borrado cuenta (para trazabilidad de acciones pasadas).

## 3. Export de datos (portabilidad)

Endpoint: `GET /me/export` (auth). Generar ZIP/JSON con todas las entidades del usuario. Formato legible, estructurado.

Incluir: perfil, lotes, checkpoints, recetas, reseñas propias, imágenes referencias, configuración.

## 4. Borrado de cuenta (derecho supresión)

Endpoint: `DELETE /me/account` con confirmación. Flujo:
1. Confirmación explícita (password/re-auth o token)
2. Borrado en transacción con orden correcto (dependencias)
3. Borrar archivos (imágenes)
4. Revocar todos refresh tokens
5. Marcar/loggear acción (anonimizada)
6. Respuesta 204

Cascada verificable por tests.

## 5. Retención y excepciones

- Moderación: conservar logs anónimos
- Seguridad: prevenir abuso (rate-limit registros)
- Datos fiscales (futuro) pueden requerir retención mínima

## 6. DoD 0H

- [ ] Matriz datos por entidad completa
- [ ] Especificación export JSON legible
- [ ] Flujo borrado con cascada
- [ ] Tests verificables (export contiene todo, borrado elimina/cascada correcta)
- [ ] Política retención documentada
- [ ] Prepara Sprint 5

## Referencias
- GDPR Art. 17/20: https://gdpr-info.eu/art-17-gdpr/
- AEPD: https://www.aepd.es/es
- docs/PLAN_SPRINTS.md FASE 0 - 0H, Sprint 5
