// Módulo de utilidades para Conservas del Mundo
// Extraído de app.js para mejor mantenibilidad

// Escapar HTML para prevenir XSS
function esc(text) {
    const div = document.createElement("div");
    div.textContent = text ?? "";
    return div.innerHTML;
}

// Escapar atributos HTML
function escAttr(text) {
    return (text ?? "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#39;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Mostrar toast
function showToast(message, type = "ok", ms = 3200) {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const el = document.createElement("div");
    el.className = `toast ${type === "err" ? "err" : type === "info" ? "info" : ""}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => {
        el.classList.add("out");
        setTimeout(() => el.remove(), 350);
    }, ms);
}

// Debounce
function debounce(fn, wait) {
    let t;
    return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn(...args), wait);
    };
}

// Crear tag
function tag(text, cls = "") {
    return `<span class="tag ${cls}">${esc(text)}</span>`;
}

// Badges de dieta
function dietBadges(tags) {
    const labels = dietLabels[state.lang] || dietLabels.es;
    return (tags || []).map((t) => tag(labels[t] || t, "diet")).join("");
}

// Badge de indicación geográfica
function giBadge(p) {
    const label = state.lang === 'en' ? 'Geographical Indication' : 'Indicación geográfica';
    return (p.geographical_indication || (p.dairy && p.dairy.geographical_indication))
        ? tag(label, "gi")
        : "";
}

// ===== Overlays accesibles (WCAG 2.1: 2.1.1, 2.4.3, 2.4.7) =====
const OVERLAY_SELECTOR = ".modal-overlay, #palette-overlay";
const _focusBeforeOverlay = new WeakMap();

function focusablesIn(root) {
    if (!root) return [];
    return Array.from(root.querySelectorAll(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]),' +
        ' textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )).filter((el) => el.offsetParent !== null || el === document.activeElement);
}

/**
 * Mantiene el foco dentro del overlay (2.4.3) y opcionalmente lo entra.
 * Sin `event` enfoca el primer control; con un evento Tab devuelven el foco
 * al borde correspondiente para que nunca escape del diálogo.
 */
function trapFocus(overlay, event) {
    const modal = typeof overlay === "string" ? document.getElementById(overlay) : overlay;
    if (!modal) return;
    const focusable = focusablesIn(modal);
    if (!focusable.length) {
        if (event) return;
        const card = modal.querySelector(".modal-card") || modal;
        if (!card.hasAttribute("tabindex")) card.setAttribute("tabindex", "-1");
        card.focus({ preventScroll: true });
        return;
    }
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (!event) {
        first.focus({ preventScroll: true });
        return;
    }
    if (event.shiftKey && (document.activeElement === first || !modal.contains(document.activeElement))) {
        event.preventDefault();
        last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
    }
}

/** Cierra el overlay usando su propio botón para respetar su lógica. */
function closeOverlay(overlay) {
    if (!overlay) return;
    const closer = overlay.querySelector(".modal-close");
    if (closer) closer.click();
    else overlay.classList.add("hidden");
}

function visibleOverlays() {
    return Array.from(document.querySelectorAll(OVERLAY_SELECTOR))
        .filter((o) => !o.classList.contains("hidden"));
}

/**
 * Un solo punto de control para los ~20 diálogos: quien abra un overlay
 * qualquer (cualquiera de los onclick del HTML o de app.js) recibe entrada
 * de foco, trampa de Tab, cierre con Escape y restauración del foco al
 * elemento que lo abrió.
 */
function initOverlayA11y() {
    document.addEventListener("keydown", (e) => {
        const open = visibleOverlays();
        if (!open.length) return;
        const top = open[open.length - 1];
        if (e.key === "Escape") {
            e.preventDefault();
            closeOverlay(top);
            return;
        }
        if (e.key === "Tab") trapFocus(top, e);
    });

    // Observar la clase `hidden` cubre todos los modales sin tocar sus
    // funciones de apertura: si aparece, entra el foco; si desaparece, vuelve.
    const observer = new MutationObserver((records) => {
        for (const record of records) {
            const el = record.target;
            if (!el.matches || !el.matches(OVERLAY_SELECTOR)) continue;
            if (!el.classList.contains("hidden")) {
                if (el.dataset.a11yReady === "1") continue;
                el.dataset.a11yReady = "1";
                _focusBeforeOverlay.set(el, document.activeElement);
                setTimeout(() => {
                    if (!el.classList.contains("hidden")) trapFocus(el);
                }, 0);
            } else if (el.dataset.a11yReady === "1") {
                delete el.dataset.a11yReady;
                const back = _focusBeforeOverlay.get(el);
                if (back && document.contains(back) && typeof back.focus === "function") {
                    back.focus({ preventScroll: true });
                }
            }
        }
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ["class"], subtree: true });
}

// Cerrar modal con foco
function closeModalWithFocus(modalId, event) {
    const modal = document.getElementById(modalId);
    if (event && event.target.id !== modalId && !event.target.classList.contains("modal-close")) return;
    modal.classList.add("hidden");
    if (document.activeElement) document.activeElement.blur();
}

// Llamada a API
async function api(path, opts) {
    const headers = { ...(opts && opts.headers ? opts.headers : {}) };
    const token = localStorage.getItem("pantry_auth_token");
    if (token && !headers.Authorization) headers.Authorization = `Bearer ${token}`;
    const resp = await fetch(path, { ...opts, headers });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}

// Skeleton de artículo: imagen destacada + 3 líneas de texto.
// Se usa mientras llegan los datos reales para que la pantalla no salte.
function articleSkeletons(count = 3) {
    return Array.from({ length: count }).map(() => `
        <div class="skeleton-article" aria-hidden="true">
            <div class="skeleton sk-media"></div>
            <div class="sk-meta">
                <div class="skeleton"></div>
                <div class="skeleton"></div>
            </div>
            <div class="skeleton sk-line is-title"></div>
            <div class="skeleton sk-line is-text"></div>
            <div class="skeleton sk-line is-text-short"></div>
        </div>`).join("");
}

// Mostrar skeletons
function showSkeletons(count = 8) {
    const list = document.getElementById("product-list");
    if (!list) return;
    list.innerHTML = Array.from({ length: count }).map(() => `
        <li class="product-card is-skeleton">
            <div class="skeleton sk-img"></div>
            <div style="flex:1">
                <div class="skeleton sk-line" style="width:60%"></div>
                <div class="skeleton sk-line" style="width:90%"></div>
                <div class="skeleton sk-line" style="width:40%"></div>
            </div>
        </li>`).join("");
}
