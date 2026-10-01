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

// Focus trapping para modales
function trapFocus(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    first.focus();
    function onKeydown(e) {
        if (e.key !== 'Tab') return;
        if (e.shiftKey) {
            if (document.activeElement === first) { e.preventDefault(); last.focus(); }
        } else {
            if (document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
    }
    modal.addEventListener('keydown', onKeydown);
    return () => modal.removeEventListener('keydown', onKeydown);
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
