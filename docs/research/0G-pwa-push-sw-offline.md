# 0G — PWA: Push API, Service Worker y sincronización offline

- **Tema:** FASE 0 - 0G
- **Estado:** Draft
- **Fecha:** 2026-10-03
- **Objetivo:** Completar 4.7 (push + cámara), N11. Decidir Workbox vs SW propio.

## 1. Estado actual

Existe `app/static/sw.js` (`CACHE_NAME = "conservas-world-v10"`), `manifest.json`, icons, botón instalación. Falta push notifications, cámara y sincronización offline robusta.

## 2. Push API (VAPID)

Necesario para notificación fermentación lista (N11).
- Claves VAPID (público/privado) por entorno
- Suscripción: `PushManager.subscribe({userVisibleOnly:true, applicationServerKey:...})`
- Almacenar `push_subscriptions` (endpoint, p256dh, auth) por usuario
- Envío: usar librería web-push (backend)
- Payload pequeño, `urgency`, `topic` para deduplicar

## 3. Service Worker: Workbox vs propio

**SW actual:** cache-first para GET. Problema: invalidación manual. Solución: versionado `CACHE_NAME` con hash build (M2/N7).

Opciones:
- **SW propio (mínimo):** control total, ligero. Requiere gestionar precache/runtime
- **Workbox:** estrategias probadas, menos código, background sync fácil. Añade dependencia

**Recomendación preliminar:** mantener SW propio + versionado automático (hash build) por simplicidad. Usar Workbox solo si background sync complejo crece.

## 4. Estrategias de caché

- Versionar `CACHE_NAME` con hash build (CI debe fallar si no cambia)
- `skipWaiting()` + `clients.claim()` para activar nuevo SW
- Stale-while-revalidate para recursos dinámicos (API GET no críticos)
- Network-first para datos frescos (búsqueda/listados)

## 5. Sincronización offline

Lotes/temporizadores: cola de operaciones pendientes (create/update/checkpoint) cuando offline → `Background Sync API` o reintento al reconectar (`online` event).

## 6. Cámara

Captura fotos lote (Sprint 10). Requiere permisos, `getUserMedia`/`input capture`, compresión, subida moderada.

## 7. DoD 0G

- [ ] Especificación VAPID + almacenamiento subscripciones
- [ ] Decisión Workbox vs SW propio justificada
- [ ] Estrategia caché + invalidación automática
- [ ] Prototipo mínimo (suscripción + notificación)
- [ ] Especificación background sync offline
- [ ] Cámara: requisitos y flujo

## Referencias
- MDN Push API: https://developer.mozilla.org/en-US/docs/Web/API/Push_API
- Workbox: https://developer.chrome.com/docs/workbox/
- PWABuilder: https://www.pwabuilder.com/
- docs/PLAN_SPRINTS.md FASE 0 - 0G, N11, Sprint 8/10
