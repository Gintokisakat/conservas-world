const state = {
    q: "",
    category: "",
    continent: "",
    country: "",
    source: "",
    method: "",
    diet: "",
    gi: false,
    onlyFavs: false,
    page: 1,
    pageSize: 20,
    total: 0,
    view: "list",
    lang: localStorage.getItem("pantry_lang") || "es"
};

const dietLabels = {
    es: {
        vegan: "Vegano",
        vegetarian: "Vegetariano",
        pescatarian: "Pescatariano",
        gluten_free: "Sin gluten",
        dairy_free: "Sin lácteos",
        soy_free: "Sin soja",
        nut_free: "Sin frutos secos",
        egg_free: "Sin huevo",
        spicy: "Picante"
    },
    en: {
        vegan: "Vegan",
        vegetarian: "Vegetarian",
        pescatarian: "Pescatarian",
        gluten_free: "Gluten-free",
        dairy_free: "Dairy-free",
        soy_free: "Soy-free",
        nut_free: "Nut-free",
        egg_free: "Egg-free",
        spicy: "Spicy"
    }
};

const i18n = {
    es: {
        header_sub: "Catálogo global de fermentos, encurtidos y recetas tradicionales",
        pantry_title: "✨ Mi Despensa Interactiva",
        pantry_desc: "Carga qué ingredientes o fermentados tienes a mano y te mostraremos qué puedes preparar.",
        ing_label: "🥦 Sustratos e Ingredientes (repollo, leche, soja…)",
        prod_label: "🧪 Fermentados que ya posees (miso, kimchi, kéfir…)",
        add_btn: "+ Agregar",
        export_btn: "💾 Guardar / Exportar",
        import_btn: "📥 Cargar Despensa",
        recommend_btn: "🔍 ¿Qué puedo preparar hoy?",
        timers_title: "⏱️ Mis Fermentos en Proceso",
        timers_desc: "Monitorea tus frascos en primera (F1) o segunda fermentación (F2).",
        add_timer_btn: "+ Iniciar Frasco",
        brine_calc_title: "🧮 Calculadora de Salinidad",
        brine_calc_desc: "Gramos de sal para fermentación láctica segura.",
        abv_calc_title: "🍺 Calculadora de Alcohol (% ABV)",
        abv_calc_desc: "Estimación para hidromiel, sidra, kvas o cerveza.",
        trouble_btn: "🚨 Diagnóstico de Problemas",
        microbes_btn: "🔬 Microbios Fermentadores",
        favs_btn: "❤️ Mis Favoritos",
        search_btn: "Buscar",
        random_btn: "🎲 Sorpréndeme",
        ph_banner: "🛡️ <strong>Seguridad Alimentaria:</strong> Para fermentación láctica y acética, el pH objetivo de seguridad es <strong>&lt; 4.6</strong> para inhibir esporas de <em>Clostridium botulinum</em>.",
        storage_title: "🧊 Conservación y almacenamiento:",
        fermentation_time_title: "⏱️ Tiempo de fermentación:",
        print_label_btn: "🏷️ Imprimir Etiqueta",
        fav_saved: "❤️ Guardado",
        fav_add: "🤍 Favorito",
        shopping_title: "🛒 Lista de Compras Requerida",
        shopping_desc: "Ingredientes necesarios para preparar las recetas seleccionadas:",
        seasonal_title: "🌿 Qué fermentar este mes",
        seasonal_desc: "Ingredientes de temporada y fermentos sugeridos.",
        flavormap_title: "🗺️ Mapa de sabores del mundo",
        flavormap_desc: "Perfil de sabor promedio por continente (clasificación heurística por ingredientes).",
        skip_link: "Saltar al contenido principal",
        semantic_filter: "🧠 Búsqueda semántica",
        search_placeholder: "Buscar por nombre o descripción (ej. kimchi, sauerkraut, choucroute...)",
        ing_placeholder: "Ej: repollo, zanahoria, sal...",
        prod_placeholder: "Ej: miso, kimchi, masa madre...",
        install_btn: "Instalar",
        course_title: "Curso de Fermentación",
        course_sub: "Cinco módulos desde la historia hasta recetas prácticas. Marca tu progreso y obtén tu certificado.",
        timeline_title: "🏺 Cronología de la fermentación",
        timeline_desc: "13.000 años de cerveza, queso, pan y conservas.",
        timeline_loading: "Cargando…",
        show_more: "Ver más",
        nutrition_title: "🧪 Información Nutricional (por 100 g)",
        nutrition_source: "Fuente: USDA FoodData Central (CC0)",
        nutrition_none: "Sin datos de nutrición disponibles para este ingrediente.",
        nutrition_calories: "Energía",
        nutrition_protein: "Proteínas",
        nutrition_fat: "Grasas",
        nutrition_carbs: "Carbohidratos",
        nutrition_fiber: "Fibra",
        nutrition_sodium: "Sodio",
        nutrition_potassium: "Potasio",
        nutrition_vitamin_c: "Vitamina C",
        nutrition_iron: "Hierro",
        nutrition_calcium: "Calcio",
        nutrition_zinc: "Zinc",
        nutrition_products: "Fermentos que lo utilizan",
        suggest_products: "Productos",
        suggest_ingredients: "Ingredientes",
        suggest_empty: "Sin coincidencias para «{q}»",
        export_csv: "📄 CSV",
        export_pdf: "🖨️ PDF",
        glossary_btn: "📚 Glosario",
        glossary_title: "Glosario de Fermentación",
        glossary_sub: "Términos esenciales de fermentación y conservación, con definiciones breves.",
        glossary_search: "Buscar un término…",
        glossary_empty: "No hay términos que coincidan con «{q}».",
        glossary_related: "Ver producto",
        glossary_pronounced: "Glosario",
        suggest_glossary: "Glosario",
        view_list: "Lista",
        view_map: "Mapa",
        gi_filter: "Indicación geográfica",
        map_loading: "Cargando mapa…",
        map_empty: "Sin resultados para mostrar en el mapa.",
        map_detail: "Ver detalle",
        pairings_title: "Combina bien con…",
        pairings_shared: "Comparte",
    },
    en: {
        header_sub: "Global catalog of ferments, pickles, and traditional recipes",
        pantry_title: "✨ My Interactive Pantry",
        pantry_desc: "Load what ingredients or fermented foods you have on hand, and we'll show you what you can make.",
        ing_label: "🥦 Substrates & Ingredients (cabbage, milk, soy…)",
        prod_label: "🧪 Fermentations You Already Own (miso, kimchi, kefir…)",
        add_btn: "+ Add",
        export_btn: "💾 Save / Export",
        import_btn: "📥 Load Pantry",
        recommend_btn: "🔍 What can I make today?",
        timers_title: "⏱️ My Active Ferments",
        timers_desc: "Monitor your jars in first (F1) or second fermentation (F2).",
        add_timer_btn: "+ Start Jar",
        brine_calc_title: "🧮 Salinity Calculator",
        brine_calc_desc: "Exact salt grams for safe lacto-fermentation.",
        abv_calc_title: "🍺 Alcohol Calculator (% ABV)",
        abv_calc_desc: "Estimate ABV for mead, cider, kvass, or beer.",
        trouble_btn: "🚨 Troubleshooting Guide",
        microbes_btn: "🔬 Fermenting Microbes",
        favs_btn: "❤️ My Favorites",
        search_btn: "Search",
        random_btn: "🎲 Surprise Me",
        ph_banner: "🛡️ <strong>Food Safety:</strong> Target safety pH for lactic and acetic fermentation is <strong>&lt; 4.6</strong> to inhibit <em>Clostridium botulinum</em> spores.",
        storage_title: "🧊 Storage & Shelf Life:",
        fermentation_time_title: "⏱️ Fermentation time:",
        print_label_btn: "🏷️ Print Label",
        fav_saved: "❤️ Saved",
        fav_add: "🤍 Favorite",
        shopping_title: "🛒 Shopping List",
        shopping_desc: "Ingredients needed to prepare the recommended recipes:",
        seasonal_title: "🌿 What to Ferment This Month",
        seasonal_desc: "In-season ingredients and suggested ferments.",
        flavormap_title: "🗺️ World flavor map",
        flavormap_desc: "Average flavor profile by continent (heuristic classification by ingredients).",
        skip_link: "Skip to main content",
        semantic_filter: "🧠 Semantic search",
        search_placeholder: "Search by name or description (e.g. kimchi, sauerkraut, choucroute...)",
        ing_placeholder: "E.g. cabbage, carrot, salt...",
        prod_placeholder: "E.g. miso, kimchi, sourdough...",
        install_btn: "Install",
        course_title: "Fermentation Course",
        course_sub: "Five modules from history to practical recipes. Track your progress and earn your certificate.",
        timeline_title: "🏺 A Timeline of Fermentation",
        timeline_desc: "13,000 years of beer, cheese, bread and preserves.",
        timeline_loading: "Loading…",
        show_more: "Show more",
        nutrition_title: "🧪 Nutrition Facts (per 100 g)",
        nutrition_source: "Source: USDA FoodData Central (CC0)",
        nutrition_none: "No nutrition data available for this ingredient.",
        nutrition_calories: "Energy",
        nutrition_protein: "Protein",
        nutrition_fat: "Fat",
        nutrition_carbs: "Carbohydrates",
        nutrition_fiber: "Fiber",
        nutrition_sodium: "Sodium",
        nutrition_potassium: "Potassium",
        nutrition_vitamin_c: "Vitamin C",
        nutrition_iron: "Iron",
        nutrition_calcium: "Calcium",
        nutrition_zinc: "Zinc",
        nutrition_products: "Ferments that use it",
        suggest_products: "Products",
        suggest_ingredients: "Ingredients",
        suggest_empty: "No matches for \"{q}\"",
        export_csv: "📄 CSV",
        export_pdf: "🖨️ PDF",
        glossary_btn: "📚 Glossary",
        glossary_title: "Fermentation Glossary",
        glossary_sub: "Essential terms of fermentation and preservation, with short definitions.",
        glossary_search: "Search a term…",
        glossary_empty: "No terms match \"{q}\".",
        glossary_related: "View product",
        glossary_pronounced: "Glossary",
        suggest_glossary: "Glossary",
        view_list: "List",
        view_map: "Map",
        gi_filter: "Geographical indication",
        map_loading: "Loading map…",
        map_empty: "No results to show on the map.",
        map_detail: "View details",
        pairings_title: "Pairs well with…",
        pairings_shared: "Shares",
    }
};

let chartInstances = {};
let lastStats = null;

// Register Service Worker for PWA / Offline support
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/static/sw.js").catch(() => {});
    });

    // Persist storage so the cache survives eviction
    if (navigator.storage && navigator.storage.persist) {
        navigator.storage.persist().catch(() => {});
    }

    // Install prompt (PWA)
    let deferredPrompt = null;
    window.addEventListener("beforeinstallprompt", (e) => {
        e.preventDefault();
        deferredPrompt = e;
        const btn = document.getElementById("install-btn");
        if (btn) btn.hidden = false;
    });
    window.addEventListener("appinstalled", () => {
        const btn = document.getElementById("install-btn");
        if (btn) btn.hidden = true;
        deferredPrompt = null;
    });
    document.addEventListener("click", (e) => {
        if (e.target.closest("#install-btn") && deferredPrompt) {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then(() => {
                deferredPrompt = null;
                const btn = document.getElementById("install-btn");
                if (btn) btn.hidden = true;
            });
        }
    });
}

const favorites = new Set(JSON.parse(localStorage.getItem("pantry_favs") || "[]"));

function saveFavorites() {
    localStorage.setItem("pantry_favs", JSON.stringify(Array.from(favorites)));
async function loadFlavorMap() {
    const continent = document.getElementById("flavormap-continent").value;
    const detail = document.getElementById("flavormap-detail").checked;
    const container = document.getElementById("flavormap-container");
    const isEn = state.lang === 'en';

    const axesTitles = {
        picante: isEn ? 'Spicy' : 'Picante',
        ácido: isEn ? 'Sour' : 'Ácido',
        umami: isEn ? 'Umami' : 'Umami',
        dulce: isEn ? 'Sweet' : 'Dulce',
        salado: isEn ? 'Salty' : 'Salado',
        amargo: isEn ? 'Bitter' : 'Amargo',
        fermentado: isEn ? 'Fermented' : 'Fermentado'
    };

    let data;
    try {
        const params = new URLSearchParams();
        if (continent) params.set("continent", continent);
        if (detail) params.set("detail", "1");
        data = await api(`/flavor-map${params.toString() ? "?" + params : ""}`);
    } catch (e) {
        container.innerHTML = `<p class="flavormap-empty">${isEn ? 'Could not load flavor map.' : 'No se pudo cargar el mapa de sabores.'}</p>`;
        return;
    }

    const sel = document.getElementById("flavormap-continent");
    if (sel.options.length <= 1) {
        const all = new Set(["Sin dato", ...data.continents.map(c => c.continent)]);
        all.forEach(name => {
            const opt = document.createElement("option");
            opt.value = name;
            opt.textContent = name;
            sel.appendChild(opt);
        });
    }

    if (!data.continents.length) {
        container.innerHTML = `<p class="flavormap-empty">${isEn ? 'No data for the selected filters.' : 'Sin datos para los filtros seleccionados.'}</p>`;
        return;
    }

    const axes = data.axes;
    const accent = (v) => `hsla(${Math.round((1 - v) * 130)}, 70%, 42%, ${0.35 + v * 0.65})`;

    container.innerHTML = data.continents.map(c => {
        const bars = axes.map(a => `
            <div class="flavormap-bar-row">
                <span class="flavormap-axis" title="${axesTitles[a]}">${axesTitles[a]}</span>
                <div class="flavormap-bar">
                    <div class="flavormap-bar-fill" style="width:${Math.round(c.profile[a] * 100)}%; background:${accent(c.profile[a])}"></div>
                </div>
                <span class="flavormap-val">${c.profile[a].toFixed(2)}</span>
            </div>`).join("");

        const detailRows = detail && data.detail
            ? `<div class="flavormap-detail">` + data.detail
                .filter(p => p.continent === c.continent)
                .sort((a, b) => (state.lang === 'en' ? 0 : a.name.localeCompare(b.name)))
                .slice(0, 20)
                .map(p => `<span class="flavormap-detail-item" data-id="${p.product_id}">${esc(p.name)}</span>`).join("")
                + `</div>`
            : "";

        return `
            <div class="flavormap-continent-card">
                <div class="flavormap-continent-head">
                    <h3>📍 ${esc(c.continent)} <span class="flavormap-count">${c.products} ${isEn ? 'products' : 'productos'}</span></h3>
                </div>
                <div class="flavormap-bars">${bars}</div>
                ${detailRows}
            </div>`;
    }).join("");
}

document.getElementById("flavormap-continent").addEventListener("change", loadFlavorMap);
document.getElementById("flavormap-detail").addEventListener("change", loadFlavorMap);
document.getElementById("flavormap-container").addEventListener("click", (e) => {
    const item = e.target.closest(".flavormap-detail-item");
    if (item && item.dataset.id) openDetail(parseInt(item.dataset.id, 10));
});

updateFavBadge();
}

function updateFavBadge() {
    const badge = document.getElementById("fav-count");
    if (badge) badge.textContent = favorites.size;
}

function toggleFavorite(id, event) {
    if (event) event.stopPropagation();
    if (favorites.has(id)) {
        favorites.delete(id);
    } else {
        favorites.add(id);
    }
    saveFavorites();
    if (state.onlyFavs) {
        renderFavorites();
    } else {
        const btn = document.querySelector(`.fav-toggle[data-id="${id}"]`);
        if (btn) btn.textContent = favorites.has(id) ? "❤️" : "🤍";
    }
}

document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-input-wrapper")) {
        closeSuggest();
    }
    const suggestBtn = e.target.closest(".suggest-item[data-suggest-index]");
    if (suggestBtn) {
        const idx = Number(suggestBtn.dataset.suggestIndex);
        if (suggestState.items[idx]) applySuggestion(suggestState.items[idx]);
        return;
    }
    const productCard = e.target.closest(".product-card[data-product-id]");
    if (productCard && !e.target.closest(".fav-toggle")) {
        openDetail(Number(productCard.dataset.productId));
        return;
    }
    const favBtn = e.target.closest(".fav-toggle[data-id]");
    if (favBtn) {
        toggleFavorite(Number(favBtn.dataset.id), e);
        return;
    }
    const microbeBadge = e.target.closest(".microbe-badge[data-name]");
    if (microbeBadge) {
        searchMicrobe(microbeBadge.dataset.name);
        return;
    }
    const ingredientChip = e.target.closest("[data-action='ingredient']");
    if (ingredientChip) {
        openIngredient(Number(ingredientChip.dataset.ingredientId), ingredientChip.dataset.ingredientName);
        return;
    }
    const labelBtn = e.target.closest("[data-action='label']");
    if (labelBtn) {
        openLabelModal(labelBtn.dataset.name, labelBtn.dataset.date, labelBtn.dataset.time, labelBtn.dataset.storage);
        return;
    }
    const exportCsvBtn = e.target.closest("[data-action='export-csv']");
    if (exportCsvBtn) {
        const a = document.createElement("a");
        a.href = `/products/${exportCsvBtn.dataset.id}/export?format=csv&lang=${state.lang}`;
        a.download = `producto-${exportCsvBtn.dataset.id}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        return;
    }
    const exportPdfBtn = e.target.closest("[data-action='export-pdf']");
    if (exportPdfBtn) {
        window.open(
            `/products/${exportPdfBtn.dataset.id}/export?format=pdf&lang=${state.lang}`,
            "_blank"
        );
        return;
    }
    const glossaryDetailBtn = e.target.closest("[data-action='glossary-detail']");
    if (glossaryDetailBtn) {
        openGlossaryModal({});
        return;
    }
    const glossaryProductBtn = e.target.closest("[data-action='glossary-product']");
    if (glossaryProductBtn) {
        closeGlossaryModal();
        openDetail(Number(glossaryProductBtn.dataset.id));
        return;
    }
    const pairingBtn = e.target.closest("[data-action='pairing']");
    if (pairingBtn) {
        openDetail(Number(pairingBtn.dataset.id));
        return;
    }
    const favDetailBtn = e.target.closest("[data-action='fav-detail']");
    if (favDetailBtn) {
        const id = Number(favDetailBtn.dataset.id);
        toggleFavorite(id);
        favDetailBtn.textContent = favorites.has(id) ? (i18n[state.lang] || i18n.es).fav_saved : (i18n[state.lang] || i18n.es).fav_add;
        return;
    }
    const removeTimerBtn = e.target.closest("[data-action='remove-timer']");
    if (removeTimerBtn) {
        removeTimer(Number(removeTimerBtn.dataset.index));
        return;
    }
    const addToPantryBtn = e.target.closest("[data-action='add-to-pantry']");
    if (addToPantryBtn) {
        addIngredientToPantry(addToPantryBtn.dataset.item);
        return;
    }
    const showShoppingBtn = e.target.closest("[data-action='show-shopping']");
    if (showShoppingBtn) {
        showShoppingList();
        return;
    }
    const diagnoseBtn = e.target.closest("[data-action='diagnose']");
    if (diagnoseBtn) {
        diagnoseTrouble(diagnoseBtn.dataset.type);
        return;
    }
});

async function api(path, opts) {
    const headers = { ...(opts && opts.headers ? opts.headers : {}) };
    const token = localStorage.getItem("pantry_auth_token");
    if (token && !headers.Authorization) headers.Authorization = `Bearer ${token}`;
    const resp = await fetch(path, { ...opts, headers });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}

function esc(text) {
    const div = document.createElement("div");
    div.textContent = text ?? "";
    return div.innerHTML;
}

// --- Autenticación (4.1) ---
let currentUser = null;

async function authRequest(path, body, isEn) {
    let resp;
    try {
        resp = await fetch(path, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
    } catch (e) {
        throw new Error(isEn ? "Network error" : "Error de red");
    }
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
        if (resp.status === 429) throw new Error(isEn ? "Too many attempts; wait a minute" : "Demasiados intentos; espera un minuto");
        throw new Error(data.detail || `HTTP ${resp.status}`);
    }
    return data;
}

async function doLogin(event) {
    event.preventDefault();
    const isEn = state.lang === 'en';
    const errEl = document.getElementById("auth-error");
    errEl.textContent = "";
    try {
        const data = await authRequest("/auth/login", {
            email: document.getElementById("auth-email").value.trim(),
            password: document.getElementById("auth-password").value,
        }, isEn);
        localStorage.setItem("pantry_auth_token", data.access_token);
        localStorage.setItem("pantry_auth_refresh", data.refresh_token);
        await loadSession();
        closeAuthModal();
    } catch (e) {
        errEl.textContent = e.message;
    }
}

async function doRegister(event) {
    event.preventDefault();
    const isEn = state.lang === 'en';
    const errEl = document.getElementById("auth-error");
    errEl.textContent = "";
    try {
        const data = await authRequest("/auth/register", {
            email: document.getElementById("auth-email").value.trim(),
            username: document.getElementById("auth-username").value.trim(),
            password: document.getElementById("auth-password").value,
        }, isEn);
        localStorage.setItem("pantry_auth_token", data.access_token);
        localStorage.setItem("pantry_auth_refresh", data.refresh_token);
        await loadSession();
        closeAuthModal();
    } catch (e) {
        errEl.textContent = e.message;
    }
}

function logout() {
    localStorage.removeItem("pantry_auth_token");
    localStorage.removeItem("pantry_auth_refresh");
    currentUser = null;
    renderAuthArea();
}

async function loadSession() {
    const token = localStorage.getItem("pantry_auth_token");
    if (!token) { currentUser = null; renderAuthArea(); return; }
    try {
        currentUser = await api("/auth/me");
    } catch (e) {
        // Intentar refrescar con el refresh token antes de rendirse.
        const refresh = localStorage.getItem("pantry_auth_refresh");
        if (refresh) {
            try {
                const resp = await fetch("/auth/refresh", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ refresh_token: refresh }),
                });
                if (resp.ok) {
                    const data = await resp.json();
                    localStorage.setItem("pantry_auth_token", data.access_token);
                    localStorage.setItem("pantry_auth_refresh", data.refresh_token);
                    currentUser = await api("/auth/me");
                } else { logout(); }
            } catch (e2) { logout(); }
        } else { logout(); }
    }
    renderAuthArea();
}

function renderAuthArea() {
    const area = document.getElementById("auth-area");
    const isEn = state.lang === 'en';
    if (currentUser) {
        area.innerHTML = `
            <span class="auth-user" title="${escAttr(currentUser.email)}">👤 ${esc(currentUser.username)}</span>
            <button type="button" id="logout-btn" class="theme-toggle" title="${isEn ? 'Log out' : 'Cerrar sesión'}" aria-label="${isEn ? 'Log out' : 'Cerrar sesión'}">⎋</button>`;
        document.getElementById("logout-btn").addEventListener("click", logout);
    } else {
        area.innerHTML = `
            <button type="button" id="login-open-btn" class="btn btn-sm btn-outline" style="border-color:rgba(255,255,255,0.4); color:#fff">${isEn ? 'Sign in' : 'Entrar'}</button>`;
        document.getElementById("login-open-btn").addEventListener("click", openAuthModal);
    }
}

function openAuthModal() {
    document.getElementById("auth-modal").classList.remove("hidden");
    setAuthMode("login");
}

function closeAuthModal(event) {
    if (event && event.target.id !== "auth-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("auth-modal").classList.add("hidden");
}

function setAuthMode(mode) {
    const isEn = state.lang === 'en';
    const isLogin = mode === "login";
    document.getElementById("auth-title").textContent = isLogin
        ? (isEn ? 'Sign in' : 'Iniciar sesión')
        : (isEn ? 'Create account' : 'Crear cuenta');
    document.getElementById("auth-username").parentElement.classList.toggle("hidden", isLogin);
    document.getElementById("auth-submit-btn").textContent = isLogin
        ? (isEn ? 'Sign in' : 'Entrar')
        : (isEn ? 'Create account' : 'Crear cuenta');
    document.getElementById("auth-switch-btn").textContent = isLogin
        ? (isEn ? 'No account? Create one' : '¿Sin cuenta? Crear una')
        : (isEn ? 'Already registered? Sign in' : '¿Ya registrado? Iniciar sesión');
    document.getElementById("auth-switch-btn").dataset.mode = isLogin ? "register" : "login";
    document.getElementById("auth-error").textContent = "";
}

function escAttr(text) {
    return (text ?? "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#39;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function tag(text, cls = "") {
    return `<span class="tag ${cls}">${esc(text)}</span>`;
}

function dietBadges(tags) {
    const labels = dietLabels[state.lang] || dietLabels.es;
    return (tags || []).map((t) => tag(labels[t] || t, "diet")).join("");
}

function giBadge(p) {
    const label = state.lang === 'en' ? 'Geographical Indication' : 'Indicación geográfica';
    return (p.geographical_indication || (p.dairy && p.dairy.geographical_indication))
        ? tag(label, "gi")
        : "";
}

async function loadStats() {
    try {
        const s = await api("/stats");
        document.getElementById("stats").innerHTML = `
            <span class="stat-pill"><strong>${s.products.toLocaleString()}</strong> ${state.lang === 'en' ? 'products' : 'productos'}</span>
            <span class="stat-pill"><strong>${s.countries}</strong> ${state.lang === 'en' ? 'countries' : 'países'}</span>
            <span class="stat-pill"><strong>${s.ingredients}</strong> ${state.lang === 'en' ? 'ingredients' : 'ingredientes'}</span>
            <span class="stat-pill"><strong>${s.categories}</strong> ${state.lang === 'en' ? 'categories' : 'categorías'}</span>
        `;
    } catch (e) {
        document.getElementById("stats").textContent = "API offline";
    }
}

async function loadCategories() {
    try {
        const cats = await api("/categories");
        const select = document.getElementById("category");
        select.innerHTML = `<option value="">${state.lang === 'en' ? 'All categories' : 'Todas las categorías'}</option>`;
        for (const c of cats) {
            const opt = document.createElement("option");
            opt.value = c.code;
            opt.textContent = c.name;
            select.appendChild(opt);
        }
    } catch (e) { /* ignore */ }
}

async function loadCountries() {
    try {
        const countries = await api("/countries");
        const select = document.getElementById("country");
        select.innerHTML = `<option value="">${state.lang === 'en' ? 'All countries' : 'Todos los países'}</option>`;
        for (const c of countries) {
            const opt = document.createElement("option");
            opt.value = c.name;
            opt.textContent = c.name;
            select.appendChild(opt);
        }
    } catch (e) { /* ignore */ }
}

async function loadDiets() {
    try {
        const tags = await api("/diets");
        const select = document.getElementById("diet");
        if (!select) return;
        const labels = dietLabels[state.lang] || dietLabels.es;
        select.innerHTML = `<option value="">${state.lang === 'en' ? 'All diets' : 'Todas las dietas'}</option>`;
        for (const t of tags) {
            const opt = document.createElement("option");
            opt.value = t;
            opt.textContent = labels[t] || t;
            select.appendChild(opt);
        }
    } catch (e) { /* ignore */ }
}

let seasonalLimit = 12;

async function loadSeasonal(reset = true) {
    const card = document.getElementById("seasonal-card");
    if (!card) return;
    if (reset) seasonalLimit = 12;
    try {
        const s = await api(`/seasonal?month=${new Date().getMonth() + 1}&limit=${seasonalLimit}`);
        const monthName = (s.month_name[state.lang] || s.month_name.es);
        const label = monthName.charAt(0).toUpperCase() + monthName.slice(1);
        document.getElementById("seasonal-desc").textContent =
            `${label}: ${s.total.toLocaleString()} ${state.lang === 'en' ? 'ferments in season' : 'fermentos en temporada'}`;
        document.getElementById("seasonal-ingredients").innerHTML = s.ingredients
            .slice(0, 12)
            .map((i) =>
                `<span class="chip seasonal-chip" title="${i.count} ${state.lang === 'en' ? 'products' : 'productos'}">${esc(i.name)}</span>`
            )
            .join("");
        const noDesc = state.lang === 'en' ? 'No description available.' : 'Sin descripción disponible.';
        document.getElementById("seasonal-products").innerHTML = s.products
            .map((p) => productCardHtml(p, noDesc))
            .join("");
        const moreBtn = document.getElementById("seasonal-more-btn");
        if (moreBtn) {
            moreBtn.hidden = s.total <= seasonalLimit;
            moreBtn.textContent = state.lang === 'en'
                ? `Show more (${(s.total - seasonalLimit).toLocaleString()})`
                : `Ver más (${(s.total - seasonalLimit).toLocaleString()})`;
        }
    } catch (e) { /* ignore */ }
}

const timelineCategoryLabels = {
    bebida: { es: "Bebida", en: "Drink" },
    lacteo: { es: "Lácteo", en: "Dairy" },
    salsa: { es: "Salsa", en: "Sauce" },
    panaderia: { es: "Panadería", en: "Baking" },
    encurtido: { es: "Encurtido", en: "Pickling" },
    conserva: { es: "Conserva", en: "Preserving" },
    ciencia: { es: "Ciencia", en: "Science" },
    cultura: { es: "Cultura", en: "Culture" },
};

async function loadTimeline() {
    const list = document.getElementById("timeline-list");
    if (!list) return;
    list.innerHTML = (i18n[state.lang] || i18n.es).timeline_loading || "…";
    try {
        const t = await api("/timeline");
        const isEn = state.lang === "en";
        list.innerHTML = t.events.map((e) => {
            const title = (e.title[state.lang] || e.title.es);
            const desc = (e.description[state.lang] || e.description.es);
            const era = e.era === "BCE"
                ? (isEn ? `${e.year.toLocaleString()} BCE` : `${e.year.toLocaleString()} a.C.`)
                : (isEn ? `${e.year.toLocaleString()} CE` : `${e.year.toLocaleString()} d.C.`);
            const cat = (timelineCategoryLabels[e.category] || {})[state.lang] || e.category;
            return `<article class="timeline-item">
                <div class="timeline-marker"><span class="timeline-year">${esc(era)}</span></div>
                <div class="timeline-content">
                    <h3>${esc(title)} <span class="timeline-region">${esc(e.region || "")}</span></h3>
                    <p>${esc(desc)}</p>
                    <span class="chip timeline-chip">${esc(cat)}</span>
                </div>
            </article>`;
        }).join("");
    } catch (err) {
        list.innerHTML = state.lang === "en"
            ? "Could not load the timeline."
            : "No se pudo cargar la cronología.";
    }
}

async function loadIngredientDatalist() {
    try {
        const ingredients = await api("/ingredients");
        const datalist = document.getElementById("ingredient-list");
        if (!datalist) return;
        datalist.innerHTML = ingredients
            .map((ing) => `<option value="${esc(ing.name)}">`)
            .join("");
    } catch (e) { /* ignore */ }
}

function buildQuery(page) {
    const params = new URLSearchParams();
    if (state.q) params.set("q", state.q);
    if (state.category) params.set("category", state.category);
    if (state.continent) params.set("continent", state.continent);
    if (state.country) params.set("country", state.country);
    if (state.source) params.set("source", state.source);
    if (state.method) params.set("method", state.method);
    if (state.diet) params.set("diet", state.diet);
    if (state.gi) params.set("gi", "true");
    params.set("lang", state.lang);
    params.set("page", page);
    params.set("page_size", state.pageSize);
    return params.toString();
}

async function search(page = 1) {
    state.onlyFavs = false;
    document.getElementById("fav-filter-btn").classList.remove("active");
    state.page = page;
    const list = document.getElementById("product-list");
    const q = document.getElementById("q").value.trim();
    if (state.semantic && q) {
        await searchSemantic(q);
        return;
    }
    list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'Searching ferments...' : 'Buscando fermentos y conservas...'}</li>`;
    try {
        const data = await api(`/products?${buildQuery(page)}`);
        state.total = data.total;
        renderResults(data.items);
        updatePagination();
        if (state.view === "map") loadMap();
    } catch (e) {
        list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'Error connecting to API. Check your connection.' : 'Error al conectar con la API. Verifica tu conexión.'}</li>`;
    }
}

async function searchSemantic(q) {
    const list = document.getElementById("product-list");
    list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'Analyzing text similarity...' : 'Analizando similitud de texto...'}</li>`;
    try {
        const data = await api(`/search/semantic?q=${encodeURIComponent(q)}&limit=30`);
        state.total = data.hits.length;
        renderSemanticResults(data.hits);
        updatePagination(1);
        if (state.view === "map") loadMap();
    } catch (e) {
        list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'Semantic search failed.' : 'La búsqueda semántica falló.'}</li>`;
    }
}

function renderSemanticResults(hits) {
    const list = document.getElementById("product-list");
    document.getElementById("count").textContent =
        `${state.total} ${state.lang === 'en' ? 'semantic result' : 'resultado semántico'}${state.total === 1 ? "" : "s"}`;
    if (!hits.length) {
        list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'No matches found for the semantic query.' : 'Sin coincidencias para la consulta semántica.'}</li>`;
        return;
    }
    list.innerHTML = hits.map((h) => {
        const img = h.image_url
            ? `<img class="card-img" src="${escAttr(h.image_url)}" alt="${escAttr(h.name)}" loading="lazy" onerror="this.style.display='none'">`
            : `<div class="card-img card-img-placeholder">${esc(h.name.charAt(0).toUpperCase())}</div>`;
        return `
        <li class="product-card" data-product-id="${h.product_id}">
            ${img}
            <div>
                <div class="card-header-row">
                    <h3>${esc(h.name)}</h3>
                    <span class="tag" style="background:rgba(45,90,63,0.12); color:var(--color-primary); border:1px solid rgba(45,90,63,0.25)">🧠 ${(h.score * 100).toFixed(0)}%</span>
                </div>
                <p class="desc">${esc(h.description || (state.lang === 'en' ? 'No description available.' : 'Sin descripción disponible.'))}</p>
            </div>
            <div class="tags">
                ${h.source_tag ? tag(h.source_tag, "source") : ""}
                <span class="tag" style="background:rgba(139,92,246,0.12); color:#8b5cf6; border:1px solid rgba(139,92,246,0.3)">🧠 ${state.lang === 'en' ? 'semantic' : 'semántico'}</span>
            </div>
        </li>`;
    }).join("");
}

async function renderFavorites() {
    state.onlyFavs = true;
    document.getElementById("fav-filter-btn").classList.add("active");
    const list = document.getElementById("product-list");
    const favIds = Array.from(favorites);
    if (!favIds.length) {
        document.getElementById("count").textContent = state.lang === 'en' ? "0 favorites" : "0 favoritos";
        list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'No favorites saved yet. Click ❤️ on any product card.' : 'Aún no tienes productos marcados como favoritos. Haz clic en el corazón ❤️ de cualquier producto para guardarlo aquí.'}</li>`;
        updatePagination(0);
        return;
    }

    list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'Loading your favorites...' : 'Cargando tus favoritos...'}</li>`;
    try {
        const items = await Promise.all(favIds.map((id) => api(`/products/${id}?lang=${state.lang}`).catch(() => null)));
        const validItems = items.filter(Boolean);
        state.total = validItems.length;
        document.getElementById("count").textContent = `${validItems.length} ${state.lang === 'en' ? 'favorite' : 'favorito'}${validItems.length === 1 ? "" : "s"}`;
        renderResults(validItems);
        updatePagination(1);
    } catch (e) {
        list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'Error loading favorites.' : 'Error al cargar tus favoritos.'}</li>`;
    }
}

function productCardHtml(p, noDesc) {
    const isFav = favorites.has(p.id);
    const img = p.image_url
        ? `<img class="card-img" src="${escAttr(p.image_url)}" alt="${escAttr(p.name)}" loading="lazy" onerror="this.style.display='none'">`
        : `<div class="card-img card-img-placeholder">${esc((p.substrate || p.name).charAt(0).toUpperCase())}</div>`;
    return `
    <li class="product-card" data-product-id="${p.id}">
        ${img}
        <div>
            <div class="card-header-row">
                <h3>${esc(p.name)}</h3>
                <button type="button" class="fav-toggle" data-id="${p.id}" title="Marcar como favorito">
                    ${isFav ? "❤️" : "🤍"}
                </button>
            </div>
            <p class="desc">${esc(p.description || noDesc)}</p>
        </div>
        <div class="tags">
            ${p.source_tag === "ark_of_taste" ? `<span class="tag" style="background:rgba(217,119,6,0.15); color:#b45309; border:1px solid rgba(217,119,6,0.3); font-weight:600">🏛️ Arca del Gusto</span>` : ""}
            ${p.fermentation_time ? `<span class="tag" style="background:rgba(45,90,63,0.12); color:var(--color-primary); border:1px solid rgba(45,90,63,0.25)">⏱️ ${esc(p.fermentation_time)}</span>` : ""}
            ${p.storage_life ? `<span class="tag" style="background:rgba(217,107,67,0.12); color:#d96b43; border:1px solid rgba(217,107,67,0.25)">🧊 ${esc(p.storage_life)}</span>` : ""}
            ${p.substrate ? tag(p.substrate, "substrate") : ""}
            ${p.categories.map((c) => tag(c.name)).join("")}
            ${p.countries.map((c) => tag(c.name, "country")).join("")}
            ${giBadge(p)}
            ${dietBadges(p.diet_tags)}
            ${p.source_tag && p.source_tag !== "ark_of_taste" ? tag(p.source_tag, "source") : ""}
        </div>
    </li>
    `;
}

function renderResults(items) {
    const list = document.getElementById("product-list");
    document.getElementById("count").textContent =
        `${state.total.toLocaleString()} ${state.lang === 'en' ? 'result' : 'resultado'}${state.total === 1 ? "" : "s"}`;
    if (!items.length) {
        list.innerHTML = `<li class="empty">${state.lang === 'en' ? 'No ferments found. Try adjusting your search filters.' : 'No encontramos fermentos con esos criterios. Prueba ajustando los filtros.'}</li>`;
        return;
    }
    const noDesc = state.lang === 'en' ? 'No description available.' : 'Sin descripción disponible.';
    list.innerHTML = items.map((p) => productCardHtml(p, noDesc)).join("");
}

function updatePagination(overridePages) {
    const pages = overridePages !== undefined ? overridePages : Math.max(1, Math.ceil(state.total / state.pageSize));
    document.getElementById("page-info").textContent = state.lang === 'en' ? `Page ${state.page} of ${pages}` : `Página ${state.page} de ${pages}`;
    document.getElementById("prev-btn").disabled = state.page <= 1 || state.onlyFavs;
    document.getElementById("next-btn").disabled = state.page >= pages || state.onlyFavs;
}

function updateDetailTimerEstimate(estMin, estMax) {
    const slider = document.getElementById("timer-slider");
    const out = document.getElementById("timer-estimate");
    if (!slider || !out) return;
    const temp = parseFloat(slider.value);
    if (estMin == null) {
        out.textContent = state.lang === 'en'
            ? `No declared range. Use reference times.`
            : `Sin rango declarado; usa los tiempos de referencia.`;
        return;
    }
    const factor = Math.pow(2, (21 - temp) / 10);
    const lo = Math.round(estMin * factor);
    const hi = Math.round(estMax * factor);
    out.textContent = state.lang === 'en'
        ? `≈ ${lo}–${hi} days at ${temp}°C`
        : `≈ ${lo}–${hi} días a ${temp}°C`;
}

async function openDetail(id) {
    const body = document.getElementById("detail-body");
    const t = i18n[state.lang] || i18n.es;
    document.getElementById("ingredient-modal").classList.add("hidden");
    body.innerHTML = `<p>${state.lang === 'en' ? 'Loading product info...' : 'Cargando información del fermento...'}</p>`;
    document.getElementById("detail").classList.remove("hidden");
    try {
        const [p, pairings, timer, safety, etymology] = await Promise.all([
            api(`/products/${id}?lang=${state.lang}`),
            api(`/products/${id}/pairings`).catch(() => null),
            api(`/timers/${id}?temp_c=21`).catch(() => null),
            api(`/products/${id}/safety?lang=${state.lang}`).catch(() => null),
            api(`/products/${id}/etymology?lang=${state.lang}`).catch(() => null),
        ]);
        const isFav = favorites.has(p.id);

        const section = (title, items) =>
            items && items.length ? `
                <div class="detail-section">
                    <h4>${title}</h4>
                    <ul>${items.map((i) => `<li>${esc(typeof i === "string" ? i : (i.name || i.title))}</li>`).join("")}</ul>
                </div>` : "";
        
        const refs = p.references && p.references.length ? `
            <div class="detail-section">
                <h4>${state.lang === 'en' ? 'References & Sources' : 'Referencias y Fuentes'}</h4>
                <ul>${p.references.map((r) => `
                    <li class="reference">${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a>` : esc(r.title)}${r.doi ? ` — DOI: ${esc(r.doi)}` : ""}</li>
                `).join("")}</ul>
            </div>` : "";

        const ingChips = p.ingredients && p.ingredients.length ? `
            <div class="detail-section">
                <h4>${state.lang === 'en' ? 'Key Ingredients' : 'Ingredientes clave'}</h4>
                <div class="tags">
                    ${p.ingredients.map((i) => `
                        <button type="button" class="ingredient-chip" data-action="ingredient" data-ingredient-id="${i.id}" data-ingredient-name="${escAttr(i.name)}">
                            ${esc(i.name)}
                        </button>
                    `).join("")}
                </div>
            </div>` : "";
            
        const pairingsHtml = pairings && pairings.items && pairings.items.length ? `
            <div class="detail-section">
                <h4>${t.pairings_title}</h4>
                <div class="pairing-grid">
                    ${pairings.items.map((pa) => `
                        <button type="button" class="pairing-card" data-action="pairing" data-id="${pa.id}">
                            ${pa.image_url ? `<img src="${escAttr(pa.image_url)}" alt="${escAttr(pa.name)}" loading="lazy" onerror="this.style.display='none'">` : ""}
                            <span class="pairing-name">${esc(pa.name)}</span>
                            <span class="pairing-cats">${pa.categories.map((c) => esc(c.name)).join(", ")}</span>
                            <span class="pairing-shared">${t.pairings_shared}: ${pa.shared_ingredients.map(esc).join(", ")}</span>
                        </button>
                    `).join("")}
                </div>
            </div>` : "";

        const safetyHtml = safety ? `
            <div class="detail-section safety-card">
                <h4>🛡️ ${state.lang === 'en' ? 'Safety & pH' : 'Seguridad y pH'}</h4>
                <div class="safety-risk" style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem">
                    <span class="tag" style="${safety.risk === 'medio' ? "background:rgba(217,119,6,0.15); color:#b45309; border:1px solid rgba(217,119,6,0.35)" : "background:rgba(45,90,63,0.12); color:var(--color-primary); border:1px solid rgba(45,90,63,0.25)"}">
                        ${state.lang === 'en' ? 'Risk:' : 'Riesgo:'} ${esc(safety.category)}
                    </span>
                    <span class="tag" style="background:rgba(139,92,246,0.12); color:#8b5cf6; border:1px solid rgba(139,92,246,0.3)">${safety.ph_requirement}</span>
                </div>
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(120px, 1fr)); gap:0.4rem; font-size:0.85rem; margin-bottom:0.6rem">
                    <span><strong>pH:</strong> ${safety.ph_min}–${safety.ph_max}</span>
                    <span><strong>aw:</strong> ${safety.aw_min}–${safety.aw_max}</span>
                    <span><strong>${state.lang === 'en' ? 'Salt' : 'Sal'}:</strong> ${safety.salt_pct_min}–${safety.salt_pct_max}%</span>
                    <span><strong>${state.lang === 'en' ? 'Temp' : 'Temp'}:</strong> ${safety.storage_temp_c}°C</span>
                    <span><strong>${state.lang === 'en' ? 'Shelf life' : 'Vida útil'}:</strong> ~${safety.shelf_life_days} ${state.lang === 'en' ? 'days' : 'días'}</span>
                </div>
                <ul style="margin:0; padding-left:1.1rem; font-size:0.85rem; color:var(--text-secondary)">
                    ${safety.alerts.map((a) => `<li>${esc(a)}</li>`).join("")}
                </ul>
            </div>` : "";

        const etymologyHtml = etymology ? `
            <div class="detail-section">
                <h4>💡 ${state.lang === 'en' ? 'Did you know?' : '¿Sabías que...?'}</h4>
                <p style="font-size:0.9rem; line-height:1.55; color:var(--text-secondary)">
                    <em>«${esc(etymology.text)}»</em>
                </p>
                <div style="font-size:0.8rem; color:var(--text-muted); margin-top:0.4rem">
                    🏷️ ${esc(etymology.term)} · ${esc(etymology.origin)} · ${esc(etymology.period)}
                </div>
            </div>` : "";

        body.innerHTML = `
            ${p.image_url ? `<img class="detail-img" src="${escAttr(p.image_url)}" alt="${escAttr(p.name)}" onerror="this.style.display='none'">` : ""}
            ${safetyHtml}
            ${etymologyHtml}
            <div id="reviews-section" class="detail-section" data-pid="${p.id}">
                <p style="color:var(--text-muted); font-size:0.85rem">${state.lang === 'en' ? 'Loading reviews…' : 'Cargando reseñas…'}</p>
            </div>
            <div class="card-header-row" style="align-items:center">
                <h2>${esc(p.name)}</h2>
                <div style="display:flex; gap:0.4rem; flex-wrap:wrap">
                    <button type="button" class="btn btn-outline btn-sm" data-action="export-csv" data-id="${p.id}">
                        ${t.export_csv}
                    </button>
                    <button type="button" class="btn btn-outline btn-sm" data-action="export-pdf" data-id="${p.id}">
                        ${t.export_pdf}
                    </button>
                    <button type="button" class="btn btn-outline btn-sm" data-action="glossary-detail">
                        📚
                    </button>
                    <button type="button" class="btn btn-outline btn-sm" data-action="label" data-name="${escAttr(p.name)}" data-date="${new Date().toISOString().slice(0,10)}" data-time="${escAttr(p.fermentation_time || '7-14 días')}" data-storage="${escAttr(p.storage_life || 'Refrigerado')}">
                        ${t.print_label_btn}
                    </button>
                    <button type="button" class="btn btn-outline btn-sm" data-action="fav-detail" data-id="${p.id}">
                        ${isFav ? t.fav_saved : t.fav_add}
                    </button>
                </div>
            </div>
            ${p.description ? `<p style="font-size:1.05rem; color:var(--text-secondary); margin-bottom:1rem">${esc(p.description)}</p>` : ""}
            ${p.method ? `<p style="background:var(--bg-page); padding:0.8rem; border-radius:var(--radius-sm)"><strong>${state.lang === 'en' ? 'Traditional Method:' : 'Método tradicional:'}</strong> ${esc(p.method)}</p>` : ""}
            ${p.fermentation_time ? `<p><strong>${t.fermentation_time_title}</strong> ${esc(p.fermentation_time)}</p>` : ""}
            ${timer && timer.estimated_days ? `
                <div style="background:var(--bg-page); padding:0.7rem 0.9rem; border-radius:var(--radius-sm); margin-top:0.5rem">
                    <div style="display:flex; align-items:center; gap:0.6rem; flex-wrap:wrap">
                        <label for="timer-slider" style="font-size:0.85rem; font-weight:600">🌡️ ${state.lang === 'en' ? 'Estimate at temp:' : 'Estimación a temp:'}</label>
                        <input type="range" id="timer-slider" min="4" max="45" step="1" value="21" style="flex:1; max-width:220px">
                        <span style="font-size:0.85rem; font-weight:600" id="timer-estimate"></span>
                    </div>
                </div>` : ""}
            ${p.storage_life ? `<p><strong>${t.storage_title}</strong> ${esc(p.storage_life)}</p>` : ""}
            
            <div class="tags" style="margin-top: 0.8rem">
                ${p.substrate ? tag(`${state.lang === 'en' ? 'Substrate' : 'Sustrato'}: ${p.substrate}`, "substrate") : ""}
                ${p.categories.map((c) => tag(c.name)).join("")}
                ${p.countries.map((c) => tag(c.name, "country")).join("")}
                ${giBadge(p)}
                ${dietBadges(p.diet_tags)}
            </div>

            <div class="ph-safety-banner">
                <span>${t.ph_banner}</span>
            </div>

            ${section(state.lang === 'en' ? 'Aliases / Local Names' : 'Alias / Nombres locales', p.aliases)}
            ${ingChips}
            ${section(state.lang === 'en' ? 'Fermenting Microbes' : 'Microbios fermentadores', p.microbes)}
            ${section(state.lang === 'en' ? 'Used as ingredient in' : 'Utiliza como ingrediente', p.uses)}
            ${section(state.lang === 'en' ? 'Contains ingredient' : 'Es ingrediente de', p.used_by)}
            ${refs}
            ${pairingsHtml}
        `;
        if (timer && timer.estimated_days) {
            updateDetailTimerEstimate(timer.estimated_days.min, timer.estimated_days.max);
            const slider = document.getElementById("timer-slider");
            if (slider) {
                slider.addEventListener("input", () =>
                    updateDetailTimerEstimate(timer.estimated_days.min, timer.estimated_days.max)
                );
            }
        }
        loadProductReviews(p.id);
    } catch (e) {
        body.innerHTML = `<p>${state.lang === 'en' ? 'Error loading product detail.' : 'Error al cargar el detalle del producto.'}</p>`;
    }
}

function closeDetail(event) {
    if (event && event.target.id !== "detail" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("detail").classList.add("hidden");
}

const NUTRITION_FIELDS = [
    ["calories", "nutrition_calories", "kcal"],
    ["protein_g", "nutrition_protein", "g"],
    ["fat_g", "nutrition_fat", "g"],
    ["carbs_g", "nutrition_carbs", "g"],
    ["fiber_g", "nutrition_fiber", "g"],
    ["sodium_mg", "nutrition_sodium", "mg"],
    ["potassium_mg", "nutrition_potassium", "mg"],
    ["vitamin_c_mg", "nutrition_vitamin_c", "mg"],
    ["iron_mg", "nutrition_iron", "mg"],
    ["calcium_mg", "nutrition_calcium", "mg"],
    ["zinc_mg", "nutrition_zinc", "mg"],
];

async function openIngredient(id, name) {
    const body = document.getElementById("ingredient-body");
    const t = i18n[state.lang] || i18n.es;
    document.getElementById("ingredient-modal").classList.remove("hidden");
    body.innerHTML = `<h2>🥕 ${esc(name)}</h2><p>${state.lang === 'en' ? 'Loading nutrition data...' : 'Cargando información nutricional...'}</p>`;
    try {
        const [nutrition, shelfLife] = await Promise.all([
            api(`/ingredients/${id}/nutrition`),
            api(`/ingredients/${id}/shelf-life?lang=${state.lang}`).catch(() => null),
        ]);
        const isEn = state.lang === 'en';
        let shelfHtml = "";
        if (shelfLife) {
            const fmt = (days) => {
                if (days == null) return "—";
                if (days >= 360) return `${Math.round(days / 360)} ${isEn ? 'year(s)' : 'año(s)'}`;
                if (days >= 30) return `${Math.round(days / 30)} ${isEn ? 'month(s)' : 'mes(es)'}`;
                return `${days} ${isEn ? 'days' : 'días'}`;
            };
            shelfHtml = `
                <h3 style="margin-top:0.4rem">🧊 ${isEn ? 'How long does it keep?' : '¿Cuánto dura?'}</h3>
                <table class="nutrition-table">
                    <tbody>
                        <tr><td>🧊 ${isEn ? 'Fridge' : 'Nevera'}</td><td>${fmt(shelfLife.fridge_days)}</td></tr>
                        <tr><td>❄️ ${isEn ? 'Freezer' : 'Congelador'}</td><td>${fmt(shelfLife.freezer_days)}</td></tr>
                        <tr><td>🏺 ${isEn ? 'Pantry' : 'Despensa'}</td><td>${fmt(shelfLife.pantry_days)}</td></tr>
                    </tbody>
                </table>
                <p style="color:var(--text-muted); font-size:0.85rem; margin-top:0.4rem">${esc(shelfLife.category)} — ${esc(shelfLife.notes)}</p>`;
        }
        let nutritionHtml = `<p style="color:var(--text-secondary); margin-bottom:0.6rem">${t.nutrition_none}</p>`;
        if (nutrition) {
            const rows = NUTRITION_FIELDS
                .filter(([key]) => nutrition[key] !== null && nutrition[key] !== undefined)
                .map(([key, labelKey, unit]) => {
                    const value = key === "calories" ? Math.round(nutrition[key]) : +Number(nutrition[key]).toFixed(1);
                    return `<tr><td>${t[labelKey]}</td><td>${value} ${unit}</td></tr>`;
                })
                .join("");
            nutritionHtml = `
                <h3 style="margin-top:0.4rem">${t.nutrition_title}</h3>
                <table class="nutrition-table">
                    <tbody>${rows}</tbody>
                </table>
                <p style="color:var(--text-muted); font-size:0.85rem; margin-top:0.6rem">${t.nutrition_source} — FDC ${esc(nutrition.fdc_id)}</p>`;
        }
        const products = await api(`/products?ingredient=${encodeURIComponent(name)}&page_size=10`);
        const productsHtml = products.total
            ? `<h3 style="margin-top:1.2rem">${t.nutrition_products}</h3>
               <ul class="ingredient-product-list">
                   ${products.items.map((p) => `
                       <li class="product-card" data-product-id="${p.id}">
                           <div>
                               <h3>${esc(p.name)}</h3>
                               <p class="desc">${esc(p.description || "")}</p>
                           </div>
                           <div class="tags">
                               ${p.substrate ? tag(p.substrate, "substrate") : ""}
                               ${p.categories.map((c) => tag(c.name)).join("")}
                               ${p.countries.map((c) => tag(c.name, "country")).join("")}
                               ${giBadge(p)}
                           </div>
                       </li>`).join("")}
               </ul>`
            : "";
        body.innerHTML = `<h2>🥕 ${esc(name)}</h2>${shelfHtml}${nutritionHtml}${productsHtml}`;
    } catch (e) {
        body.innerHTML = `<h2>🥕 ${esc(name)}</h2><p>${state.lang === 'en' ? 'Error loading ingredient info.' : 'Error al cargar la información del ingrediente.'}</p>`;
    }
}

function closeIngredientModal(event) {
    if (event && event.target.id !== "ingredient-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("ingredient-modal").classList.add("hidden");
}

function closeShoppingModal(event) {
    if (event && event.target.id !== "shopping-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("shopping-modal").classList.add("hidden");
}

function closeMicrobesModal(event) {
    if (event && event.target.id !== "microbes-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("microbes-modal").classList.add("hidden");
}

function closeTroubleModal(event) {
    if (event && event.target.id !== "trouble-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("trouble-modal").classList.add("hidden");
}

function closeLabelModal(event) {
    if (event && event.target.id !== "label-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("label-modal").classList.add("hidden");
}

function closeChartsModal(event) {
    if (event && event.target.id !== "charts-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("charts-modal").classList.add("hidden");
}

let guidesCache = [];
let guideState = null;

async function loadGuides() {
    try {
        guidesCache = await api(`/guides?lang=${state.lang}`);
    } catch (e) {
        guidesCache = [];
    }
}

function renderGuideList() {
    const body = document.getElementById("guide-body");
    const isEn = state.lang === 'en';
    body.innerHTML = `
        <h2>📖 ${isEn ? 'Step-by-step guides' : 'Guías paso a paso'}</h2>
        <p style="color:var(--text-secondary); margin-bottom:1.2rem">${isEn ? 'Interactive fermentation recipes with steps, timings and temperatures.' : 'Recetas interactivas de fermentación con pasos, tiempos y temperaturas.'}</p>
        <div id="guide-list" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:1rem">
            ${guidesCache.map((g) => `
                <button type="button" class="guide-card" data-slug="${escAttr(g.slug)}" style="text-align:left; cursor:pointer; background:var(--bg-page); border:1px solid var(--border-color); border-radius:var(--radius-md); padding:1rem">
                    <div style="font-size:0.78rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.04em">${esc(g.category)} · ${esc(g.difficulty)}</div>
                    <h3 style="margin:0.3rem 0 0.4rem; color:var(--color-primary)">${esc(g.title)}</h3>
                    <p style="font-size:0.88rem; color:var(--text-secondary); margin:0 0 0.5rem">${esc(g.intro)}</p>
                    <span class="tag" style="background:rgba(45,90,63,0.12); color:var(--color-primary); border:1px solid rgba(45,90,63,0.25)">⏱️ ${g.total_min} ${isEn ? 'min' : 'min'} · ${g.steps} ${isEn ? 'steps' : 'pasos'}</span>
                </button>`).join("") || `<p style="color:var(--text-muted)">${isEn ? 'No guides available.' : 'No hay guías disponibles.'}</p>`}
        </div>`;
    body.querySelectorAll(".guide-card").forEach((card) => {
        card.addEventListener("click", () => openGuide(card.dataset.slug));
    });
}

async function openGuide(slug) {
    const body = document.getElementById("guide-body");
    const isEn = state.lang === 'en';
    body.innerHTML = `<p style="color:var(--text-muted)">${isEn ? 'Loading guide...' : 'Cargando guía...'}</p>`;
    let g;
    try {
        g = await api(`/guides/${slug}?lang=${state.lang}`);
    } catch (e) {
        body.innerHTML = `<p style="color:var(--text-muted)">${isEn ? 'Could not load guide.' : 'No se pudo cargar la guía.'}</p>`;
        return;
    }
    guideState = { guide: g, index: 0 };
    renderGuideStep();
}

function guideTimerLabel(step) {
    const isEn = state.lang === 'en';
    let s = "";
    if (step.temp_c != null) s += `${isEn ? 'at' : 'a'} ${step.temp_c}°C `;
    if (step.duration_min != null) s += `· ${step.duration_min} ${isEn ? 'min' : 'min'}`;
    return s.trim();
}

function renderGuideStep() {
    if (!guideState) return;
    const body = document.getElementById("guide-body");
    const isEn = state.lang === 'en';
    const g = guideState.guide;
    const step = g.steps[guideState.index];
    const pct = Math.round(((guideState.index + 1) / g.steps.length) * 100);

    const safetyHtml = step.safety ? `<p style="margin-top:0.8rem; padding:0.6rem 0.8rem; border-radius:var(--radius-sm); background:rgba(217,119,6,0.12); border:1px solid rgba(217,119,6,0.3); color:#b45309; font-size:0.88rem">⚠️ ${isEn ? 'Safety check: never taste if the brine smells foul or has black mold.' : 'Control de inocuidad: nunca pruebes si la salmuera huele mal o tiene moho negro.'}</p>` : "";

    body.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.6rem; margin-bottom:0.6rem">
            <button type="button" class="btn btn-sm btn-outline" id="guide-back-btn">← ${isEn ? 'All guides' : 'Todas las guías'}</button>
            <span class="tag" style="background:rgba(45,90,63,0.12); color:var(--color-primary); border:1px solid rgba(45,90,63,0.25)">${esc(g.category)} · ${esc(g.difficulty)}</span>
        </div>
        <h2 style="margin:0 0 0.2rem">${esc(g.title)}</h2>
        <div class="guide-progress" style="height:8px; background:var(--border-color); border-radius:4px; margin:0.8rem 0">
            <div style="height:100%; width:${pct}%; background:var(--color-accent); border-radius:4px; transition:width 0.3s ease"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:var(--text-muted); margin-bottom:1rem">
            <span>${isEn ? 'Step' : 'Paso'} ${step.number} ${isEn ? 'of' : 'de'} ${g.steps.length}</span>
            <span>${guideTimerLabel(step)}</span>
        </div>
        <h3 style="color:var(--color-primary); margin:0 0 0.6rem">${step.number}. ${esc(step.title)}</h3>
        <p style="line-height:1.6; color:var(--text-color)">${esc(step.body)}</p>
        ${safetyHtml}
        <div style="display:flex; gap:0.6rem; margin-top:1.2rem; flex-wrap:wrap">
            ${step.duration_min ? `<button type="button" class="btn btn-secondary" id="guide-timer-btn">⏱️ ${isEn ? 'Start timer' : 'Iniciar temporizador'} (${step.duration_min} min)</button>` : ""}
            <button type="button" class="btn btn-outline" id="guide-prev-btn" ${guideState.index === 0 ? "disabled" : ""}>← ${isEn ? 'Prev' : 'Anterior'}</button>
            <button type="button" class="btn btn-primary" id="guide-next-btn" style="margin-left:auto">${guideState.index < g.steps.length - 1 ? (isEn ? 'Next step →' : 'Siguiente paso →') : (isEn ? 'Finish ✓' : 'Finalizar ✓')}</button>
        </div>`;

    document.getElementById("guide-back-btn").addEventListener("click", renderGuideList);
    const timerBtn = document.getElementById("guide-timer-btn");
    if (timerBtn) {
        timerBtn.addEventListener("click", () => {
            const t = guideState.guide;
            timers.push({
                name: `${t.title} — ${isEn ? 'step' : 'paso'} ${step.number}`,
                days: Math.max(1, Math.ceil(step.duration_min / 1440)),
                tempC: step.temp_c || 21,
                notes: isEn ? `Guide step ${step.number}` : `Paso ${step.number} de la guía`,
                startDate: Date.now()
            });
            saveTimers();
            renderTimers();
        });
    }
    document.getElementById("guide-prev-btn").addEventListener("click", () => {
        if (guideState.index > 0) { guideState.index--; renderGuideStep(); }
    });
    document.getElementById("guide-next-btn").addEventListener("click", () => {
        if (guideState.index < guideState.guide.steps.length - 1) {
            guideState.index++;
            renderGuideStep();
        } else {
            renderGuideList();
        }
    });
}

function openGuideModal() {
    document.getElementById("guide-modal").classList.remove("hidden");
    renderGuideList();
}

function closeGuideModal(event) {
    if (event && event.target.id !== "guide-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("guide-modal").classList.add("hidden");
}

// --- Curso de fermentación (4.4) ---
let courseCache = [];
let courseState = null;

async function loadCourse() {
    try {
        courseCache = await api(`/course?lang=${state.lang}`);
    } catch (e) {
        courseCache = [];
    }
}

function courseDifficultyLabel(d) {
    const isEn = state.lang === 'en';
    return ["", "★", "★★", "★★★"][d] || "★";
}

function renderCourseList() {
    const body = document.getElementById("course-body");
    const isEn = state.lang === 'en';
    const progress = JSON.parse(localStorage.getItem("pantry_course_progress") || "{}");
    body.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.6rem; margin-bottom:1rem">
            <div>
                <h2 style="margin:0">🎓 ${isEn ? 'Fermentation Course' : 'Curso de Fermentación'}</h2>
                <p style="color:var(--text-secondary); margin:0.2rem 0 0">${isEn ? 'Five modules from history to practical recipes. Track your progress.' : 'Cinco módulos desde la historia hasta recetas prácticas. Sigue tu progreso.'}</p>
            </div>
            <button type="button" class="btn btn-sm btn-outline" id="course-cert-btn">📜 ${isEn ? 'My certificate' : 'Mi certificado'}</button>
        </div>
        <div id="course-list" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:1rem">
            ${courseCache.map((m) => {
                const done = (progress[m.slug] || []).length;
                const total = m.lesson_count;
                return `<div class="guide-card" style="background:var(--bg-page); border:1px solid var(--border-color); border-radius:var(--radius-md); padding:1rem">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <span class="tag" style="background:rgba(45,90,63,0.12); color:var(--color-primary); border:1px solid rgba(45,90,63,0.25)">${courseDifficultyLabel(m.difficulty)} · ${m.estimated_hours}${isEn ? 'h' : 'h'}</span>
                        <span style="font-size:0.8rem; color:var(--text-muted)">${done}/${total}</span>
                    </div>
                    <h3 style="margin:0.5rem 0 0.3rem; color:var(--color-primary)">${esc(m.title)}</h3>
                    <p style="font-size:0.88rem; color:var(--text-secondary); margin:0 0 0.6rem">${esc(m.subtitle)}</p>
                    <div style="height:6px; background:var(--border-color); border-radius:3px; overflow:hidden">
                        <div style="height:100%; width:${total ? Math.round(done / total * 100) : 0}%; background:var(--color-accent)"></div>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline" data-course-slug="${escAttr(m.slug)}" style="margin-top:0.7rem; width:100%">${isEn ? 'Open module →' : 'Abrir módulo →'}</button>
                </div>`;
            }).join("") || `<p style="color:var(--text-muted)">${isEn ? 'Course unavailable.' : 'Curso no disponible.'}</p>`}
        </div>`;
    body.querySelectorAll("[data-course-slug]").forEach((btn) => {
        btn.addEventListener("click", () => openCourseModule(btn.dataset.courseSlug));
    });
    const certBtn = document.getElementById("course-cert-btn");
    if (certBtn) certBtn.addEventListener("click", showCourseCertificate);
}

async function openCourseModule(slug) {
    const body = document.getElementById("course-body");
    const isEn = state.lang === 'en';
    body.innerHTML = `<p style="color:var(--text-muted)">${isEn ? 'Loading module...' : 'Cargando módulo...'}</p>`;
    let m;
    try {
        m = await api(`/course/${slug}?lang=${state.lang}`);
    } catch (e) {
        body.innerHTML = `<p style="color:var(--text-muted)">${isEn ? 'Could not load module.' : 'No se pudo cargar el módulo.'}</p>`;
        return;
    }
    courseState = { module: m, index: 0 };
    renderCourseLesson();
}

function renderCourseLesson() {
    if (!courseState) return;
    const body = document.getElementById("course-body");
    const isEn = state.lang === 'en';
    const m = courseState.module;
    const lesson = m.lessons[courseState.index];
    const progress = JSON.parse(localStorage.getItem("pantry_course_progress") || "{}");
    const doneSet = new Set(progress[m.slug] || []);

    body.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.6rem; margin-bottom:0.6rem">
            <button type="button" class="btn btn-sm btn-outline" id="course-back-btn">← ${isEn ? 'All modules' : 'Todos los módulos'}</button>
            <span class="tag" style="background:rgba(45,90,63,0.12); color:var(--color-primary); border:1px solid rgba(45,90,63,0.25)">${courseDifficultyLabel(m.difficulty)} · ${m.estimated_hours}${isEn ? 'h' : 'h'}</span>
        </div>
        <h2 style="margin:0 0 0.2rem">${esc(m.title)}</h2>
        <p style="color:var(--text-secondary); margin:0 0 0.8rem; font-size:0.9rem">${esc(m.subtitle)}</p>
        <div style="height:8px; background:var(--border-color); border-radius:4px; margin:0.8rem 0">
            <div style="height:100%; width:${Math.round(((courseState.index + 1) / m.lessons.length) * 100)}%; background:var(--color-accent); border-radius:4px; transition:width 0.3s ease"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:var(--text-muted); margin-bottom:1rem">
            <span>${isEn ? 'Lesson' : 'Lección'} ${courseState.index + 1} ${isEn ? 'of' : 'de'} ${m.lessons.length} · ⏱️ ${lesson.duration_min} min</span>
        </div>
        <h3 style="color:var(--color-primary); margin:0 0 0.8rem">${esc(lesson.title)}</h3>
        ${lesson.sections.map((s) => `
            <div style="margin-bottom:1rem">
                <h4 style="margin:0 0 0.3rem">${esc(s.heading)}</h4>
                <p style="line-height:1.6; margin:0 0 0.4rem">${esc(s.body)}</p>
                ${s.bullets.length ? `<ul style="margin:0.3rem 0 0; padding-left:1.2rem; line-height:1.6; color:var(--text-secondary); font-size:0.9rem">${s.bullets.map((b) => `<li>${esc(b)}</li>`).join("")}</ul>` : ""}
            </div>`).join("")}
        <div style="display:flex; gap:0.6rem; margin-top:1.2rem; flex-wrap:wrap; align-items:center">
            <label style="display:flex; align-items:center; gap:0.4rem; font-size:0.9rem; cursor:pointer">
                <input type="checkbox" id="course-done-check" ${doneSet.has(lesson.slug) ? "checked" : ""}> ${isEn ? 'Mark as complete' : 'Marcar como completada'}
            </label>
            <button type="button" class="btn btn-outline" id="course-prev-btn" ${courseState.index === 0 ? "disabled" : ""}>← ${isEn ? 'Prev' : 'Anterior'}</button>
            <button type="button" class="btn btn-primary" id="course-next-btn" style="margin-left:auto">${courseState.index < m.lessons.length - 1 ? (isEn ? 'Next lesson →' : 'Siguiente lección →') : (isEn ? 'Finish module ✓' : 'Terminar módulo ✓')}</button>
        </div>`;

    document.getElementById("course-back-btn").addEventListener("click", renderCourseList);
    document.getElementById("course-done-check").addEventListener("change", (e) => {
        const slug = lesson.slug;
        const prog = JSON.parse(localStorage.getItem("pantry_course_progress") || "{}");
        const set = new Set(prog[m.slug] || []);
        if (e.target.checked) set.add(slug); else set.delete(slug);
        prog[m.slug] = [...set];
        localStorage.setItem("pantry_course_progress", JSON.stringify(prog));
    });
    document.getElementById("course-prev-btn").addEventListener("click", () => {
        if (courseState.index > 0) { courseState.index--; renderCourseLesson(); }
    });
    document.getElementById("course-next-btn").addEventListener("click", () => {
        if (courseState.index < m.lessons.length - 1) {
            courseState.index++;
            renderCourseLesson();
        } else {
            renderCourseList();
        }
    });
}

function showCourseCertificate() {
    const body = document.getElementById("course-body");
    const isEn = state.lang === 'en';
    const progress = JSON.parse(localStorage.getItem("pantry_course_progress") || "{}");
    const total = courseCache.reduce((a, m) => a + m.lesson_count, 0);
    const done = courseCache.reduce((a, m) => a + (progress[m.slug] || []).length, 0);
    const pct = total ? Math.round((done / total) * 100) : 0;
    const completed = pct === 100;
    body.innerHTML = `
        <div style="text-align:center; padding:1.5rem">
            <button type="button" class="btn btn-sm btn-outline" id="cert-back-btn" style="float:left">← ${isEn ? 'All modules' : 'Todos los módulos'}</button>
            <div style="margin-top:1rem; max-width:520px; margin-left:auto; margin-right:auto; border:2px solid var(--color-primary); border-radius:var(--radius-md); padding:2rem; background:var(--bg-page)">
                <div style="font-size:2rem">🏅</div>
                <h2 style="margin:0.5rem 0 0.2rem">${isEn ? 'Fermentation Course' : 'Curso de Fermentación'}</h2>
                <p style="color:var(--text-secondary)">${isEn ? 'Certificate of completion' : 'Certificado de finalización'}</p>
                <p style="margin:1rem 0">${done} / ${total} ${isEn ? 'lessons completed' : 'lecciones completadas'} (${pct}%)</p>
                <div style="height:10px; background:var(--border-color); border-radius:5px; overflow:hidden; margin-bottom:1rem">
                    <div style="height:100%; width:${pct}%; background:${completed ? "var(--color-accent)" : "var(--color-primary)"}"></div>
                </div>
                ${completed
                    ? `<p style="color:var(--color-primary); font-weight:600">✓ ${isEn ? 'Congratulations! You completed the course.' : '¡Enhorabuena! Has completado el curso.'}</p>`
                    : `<p style="color:var(--text-secondary); font-size:0.9rem">${isEn ? 'Complete all lessons to earn your certificate.' : 'Completa todas las lecciones para obtener tu certificado.'}</p>`}
                <button type="button" class="btn btn-primary" onclick="window.print()">🖨️ ${isEn ? 'Print certificate' : 'Imprimir certificado'}</button>
            </div>
        </div>`;
    document.getElementById("cert-back-btn").addEventListener("click", renderCourseList);
}

function openCourseModal() {
    document.getElementById("course-modal").classList.remove("hidden");
    renderCourseList();
}

function closeCourseModal(event) {
    if (event && event.target.id !== "course-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("course-modal").classList.add("hidden");
}

// --- Podcast (4.5) ---
let podcastTopics = { topics: [], ferments: [] };
let podcastFilter = { topic: "", ferment: "" };

async function loadPodcastTopics() {
    try {
        podcastTopics = await api(`/podcast/topics?lang=${state.lang}`);
    } catch (e) {
        podcastTopics = { topics: [], ferments: [] };
    }
}

function renderPodcastList() {
    const body = document.getElementById("podcast-body");
    const isEn = state.lang === 'en';
    body.innerHTML = `
        <h2>🎙️ ${isEn ? 'Fermentation Podcasts' : 'Podcasts de fermentación'}</h2>
        <p style="color:var(--text-secondary); margin-bottom:1rem">${isEn ? 'Curated episodes from FermUp and Ferment Radio. External links — no audio is embedded.' : 'Episodios seleccionados de FermUp y Ferment Radio. Enlaces externos: no se incrusta audio.'}</p>
        <div style="display:flex; gap:0.6rem; flex-wrap:wrap; margin-bottom:1rem">
            <select id="podcast-topic-filter" class="lang-picker" style="padding:0.45rem 0.7rem; border-radius:var(--radius-sm); border:1px solid var(--border-color)">
                <option value="">${isEn ? 'All topics' : 'Todos los temas'}</option>
                ${podcastTopics.topics.map((t) => `<option value="${escAttr(t.key)}">${esc(t.label)}</option>`).join("")}
            </select>
            <select id="podcast-ferment-filter" class="lang-picker" style="padding:0.45rem 0.7rem; border-radius:var(--radius-sm); border:1px solid var(--border-color)">
                <option value="">${isEn ? 'All ferments' : 'Todos los fermentos'}</option>
                ${podcastTopics.ferments.map((f) => `<option value="${escAttr(f)}">${esc(f)}</option>`).join("")}
            </select>
            <button type="button" class="btn btn-sm btn-outline" id="podcast-clear-btn">${isEn ? 'Clear' : 'Limpiar'}</button>
        </div>
        <div id="podcast-loading" class="hidden" role="status" aria-live="polite">${isEn ? 'Loading episodes…' : 'Cargando episodios…'}</div>
        <div id="podcast-list" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:1rem"></div>`;

    document.getElementById("podcast-topic-filter").addEventListener("change", (e) => {
        podcastFilter.topic = e.target.value;
        renderPodcastEpisodes();
    });
    document.getElementById("podcast-ferment-filter").addEventListener("change", (e) => {
        podcastFilter.ferment = e.target.value;
        renderPodcastEpisodes();
    });
    document.getElementById("podcast-clear-btn").addEventListener("click", () => {
        podcastFilter = { topic: "", ferment: "" };
        document.getElementById("podcast-topic-filter").value = "";
        document.getElementById("podcast-ferment-filter").value = "";
        renderPodcastEpisodes();
    });
    renderPodcastEpisodes();
}

async function renderPodcastEpisodes() {
    const isEn = state.lang === 'en';
    const listEl = document.getElementById("podcast-list");
    const loadingEl = document.getElementById("podcast-loading");
    if (!listEl) return;
    loadingEl.classList.remove("hidden");
    let eps = [];
    try {
        const params = new URLSearchParams({ lang: state.lang });
        if (podcastFilter.topic) params.set("topic", podcastFilter.topic);
        if (podcastFilter.ferment) params.set("ferment", podcastFilter.ferment);
        eps = await api(`/podcast?${params.toString()}`);
    } catch (e) {
        eps = [];
    }
    loadingEl.classList.add("hidden");
    listEl.innerHTML = eps.map((e) => `
        <div class="guide-card" style="background:var(--bg-page); border:1px solid var(--border-color); border-radius:var(--radius-md); padding:1rem; display:flex; flex-direction:column">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem">
                <span class="tag" style="background:rgba(45,90,63,0.12); color:var(--color-primary); border:1px solid rgba(45,90,63,0.25)">${esc(e.show)} #${e.number}</span>
                <span style="font-size:0.8rem; color:var(--text-muted)">${e.duration_min ? `⏱️ ${e.duration_min} min` : ""}</span>
            </div>
            <h3 style="margin:0 0 0.3rem; color:var(--color-primary)">${esc(e.title)}</h3>
            <p style="font-size:0.88rem; color:var(--text-secondary); margin:0 0 0.6rem; flex:1">${esc(e.summary)}</p>
            <div style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.8rem">
                ${e.ferments.map((f) => `<button type="button" class="podcast-ferment-tag tag" data-ferment="${escAttr(f)}" style="background:rgba(217,107,67,0.12); color:#d96b43; border:1px solid rgba(217,107,67,0.3); cursor:pointer">#${esc(f)}</button>`).join("")}
            </div>
            <a class="btn btn-sm btn-outline" href="${escAttr(e.url)}" target="_blank" rel="noopener noreferrer" style="text-align:center">${isEn ? 'Listen on the source site ↗' : 'Escuchar en el sitio de origen ↗'}</a>
        </div>`).join("") || `<p style="color:var(--text-muted)">${isEn ? 'No episodes found.' : 'No hay episodios para esos filtros.'}</p>`;
    listEl.querySelectorAll(".podcast-ferment-tag").forEach((btn) => {
        btn.addEventListener("click", () => {
            const q = document.getElementById("search-input");
            if (q) q.value = btn.dataset.ferment;
            document.getElementById("podcast-modal").classList.add("hidden");
            search(1);
        });
    });
}

function openPodcastModal() {
    document.getElementById("podcast-modal").classList.remove("hidden");
    renderPodcastList();
}

function closePodcastModal(event) {
    if (event && event.target.id !== "podcast-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("podcast-modal").classList.add("hidden");
}

// --- Reseñas (4.2) ---
function starsText(rating) {
    return "★".repeat(rating) + "☆".repeat(5 - rating);
}

async function apiSend(method, path, body) {
    const headers = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    const token = localStorage.getItem("pantry_auth_token");
    if (token) headers.Authorization = `Bearer ${token}`;
    const resp = await fetch(path, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (!resp.ok) {
        let detail = `HTTP ${resp.status}`;
        try {
            const data = await resp.json();
            if (data.detail) detail = data.detail;
        } catch (e) { /* sin cuerpo JSON */ }
        throw new Error(detail);
    }
    return resp.status;
}

function reviewsI18n() {
    const isEn = state.lang === 'en';
    return {
        title: isEn ? 'Reviews' : 'Reseñas',
        none: isEn ? 'No reviews yet. Be the first!' : 'Aún no hay reseñas. ¡Sé el primero!',
        loginFirst: isEn ? 'Sign in to review' : 'Entrar para reseñar',
        yourRating: isEn ? 'Your rating' : 'Tu valoración',
        placeholder: isEn ? 'Optional comment…' : 'Comentario opcional…',
        submit: isEn ? 'Publish review' : 'Publicar reseña',
        update: isEn ? 'Update review' : 'Actualizar reseña',
        edit: isEn ? 'Edit' : 'Editar',
        del: isEn ? 'Delete' : 'Eliminar',
        cancel: isEn ? 'Cancel' : 'Cancelar',
        you: isEn ? 'You' : 'Tú',
    };
}

async function loadProductReviews(pid, editingId) {
    const sectionEl = document.getElementById("reviews-section");
    if (!sectionEl || Number(sectionEl.dataset.pid) !== pid) return;
    const T = reviewsI18n();
    const isEn = state.lang === 'en';
    let data = { total: 0, average: null, items: [] };
    try {
        data = await api(`/products/${pid}/reviews`);
    } catch (e) { /* la sección queda vacía */ }

    const mine = currentUser ? data.items.find((r) => r.mine) : null;
    const editing = editingId != null && mine && mine.id === editingId ? mine : null;

    const listHtml = data.items.length
        ? `<div style="display:flex; flex-direction:column; gap:0.6rem; margin-top:0.6rem">
            ${data.items.map((r) => `
                <div style="border:1px solid var(--border-color); border-radius:var(--radius-sm); padding:0.6rem 0.8rem">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:0.5rem">
                        <span style="color:#e8b45a; letter-spacing:1px">${starsText(r.rating)}</span>
                        <span style="font-size:0.78rem; color:var(--text-muted)">
                            ${r.mine ? T.you : "👤"} · ${(r.created_at || "").slice(0, 10)}
                            ${r.mine ? `
                                <button type="button" class="btn btn-sm btn-outline" data-review-edit="${r.id}" style="margin-left:0.4rem; padding:0.1rem 0.5rem">${T.edit}</button>
                                <button type="button" class="btn btn-sm btn-outline" data-review-del="${r.id}" style="padding:0.1rem 0.5rem">${T.del}</button>` : ""}
                        </span>
                    </div>
                    ${r.text ? `<p style="font-size:0.88rem; margin:0.3rem 0 0; line-height:1.5">${esc(r.text)}</p>` : ""}
                </div>`).join("")}
        </div>`
        : `<p style="color:var(--text-muted); font-size:0.85rem; margin-top:0.4rem">${T.none}</p>`;

    const avgHtml = data.average != null
        ? `<span style="color:#e8b45a; font-weight:600">★ ${data.average}</span><span style="color:var(--text-muted); font-size:0.82rem"> · ${data.total} ${isEn ? (data.total === 1 ? 'review' : 'reviews') : (data.total === 1 ? 'reseña' : 'reseñas')}</span>`
        : "";

    const formHtml = !currentUser
        ? `<button type="button" id="review-login-btn" class="btn btn-sm btn-outline" style="margin-top:0.6rem">🔐 ${T.loginFirst}</button>`
        : (!mine || editing)
            ? `<div style="margin-top:0.7rem">
                <div id="review-stars" style="display:flex; gap:0.15rem; font-size:1.3rem; cursor:pointer; color:#e8b45a" data-value="${editing ? editing.rating : 0}">
                    ${[1, 2, 3, 4, 5].map((v) => `<span data-star="${v}">☆</span>`).join("")}
                </div>
                <textarea id="review-text" maxlength="4000" rows="2" placeholder="${T.placeholder}"
                    style="width:100%; margin-top:0.4rem; border:1px solid var(--border-color); border-radius:var(--radius-sm); background:var(--bg-page); color:var(--text-color); padding:0.5rem; font-family:inherit"></textarea>
                <p id="review-error" style="color:#d96b43; font-size:0.8rem; min-height:1rem; margin:0.2rem 0"></p>
                <div style="display:flex; gap:0.5rem">
                    <button type="button" id="review-submit-btn" class="btn btn-sm btn-primary" data-editing="${editing ? editing.id : ""}">${editing ? T.update : T.submit}</button>
                    ${editing ? `<button type="button" id="review-cancel-btn" class="btn btn-sm btn-outline">${T.cancel}</button>` : ""}
                </div>
            </div>`
            : "";

    sectionEl.innerHTML = `
        <h4>⭐ ${T.title} ${avgHtml}</h4>
        ${listHtml}
        ${formHtml}`;

    bindReviewEvents(pid);
}

function paintStars(value) {
    document.querySelectorAll("#review-stars [data-star]").forEach((el) => {
        el.textContent = Number(el.dataset.star) <= value ? "★" : "☆";
    });
}

function bindReviewEvents(pid) {
    const sectionEl = document.getElementById("reviews-section");
    if (!sectionEl) return;

    const loginBtn = document.getElementById("review-login-btn");
    if (loginBtn) loginBtn.addEventListener("click", openAuthModal);

    const stars = document.getElementById("review-stars");
    if (stars) {
        stars.querySelectorAll("[data-star]").forEach((el) => {
            el.addEventListener("click", () => {
                stars.dataset.value = el.dataset.star;
                paintStars(Number(el.dataset.star));
            });
        });
        if (Number(stars.dataset.value)) paintStars(Number(stars.dataset.value));
    }

    const submitBtn = document.getElementById("review-submit-btn");
    if (submitBtn) submitBtn.addEventListener("click", async () => {
        const rating = Number(document.getElementById("review-stars").dataset.value);
        const text = document.getElementById("review-text").value.trim() || null;
        const errEl = document.getElementById("review-error");
        errEl.textContent = "";
        if (!rating) {
            errEl.textContent = state.lang === 'en' ? 'Pick a star rating.' : 'Elegí una valoración de estrellas.';
            return;
        }
        const editingId = submitBtn.dataset.editing;
        try {
            if (editingId) {
                await apiSend("PUT", `/reviews/${editingId}`, { rating, text });
                await loadProductReviews(pid, null);
            } else {
                await apiSend("POST", `/products/${pid}/reviews`, { rating, text });
                await loadProductReviews(pid);
            }
        } catch (e) {
            errEl.textContent = e.message;
        }
    });

    const cancelBtn = document.getElementById("review-cancel-btn");
    if (cancelBtn) cancelBtn.addEventListener("click", () => loadProductReviews(pid));

    sectionEl.querySelectorAll("[data-review-edit]").forEach((btn) => {
        btn.addEventListener("click", () => loadProductReviews(pid, Number(btn.dataset.reviewEdit)));
    });
    sectionEl.querySelectorAll("[data-review-del]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            if (!confirm(state.lang === 'en' ? 'Delete your review?' : '¿Eliminar tu reseña?')) return;
            try {
                await apiSend("DELETE", `/reviews/${btn.dataset.reviewDel}`);
                await loadProductReviews(pid);
            } catch (e) { /* noop */ }
        });
    });
}

// --- Recetas comunitarias (4.3) ---
let recipesFilter = { q: "", difficulty: "", sort: "votes", page: 1 };

function recipesI18nT() {
    const isEn = state.lang === 'en';
    return {
        title: isEn ? 'Community Recipes' : 'Recetas comunitarias',
        sub: isEn ? 'Fermentation recipes shared by the community.' : 'Recetas de fermentación compartidas por la comunidad.',
        newRecipe: isEn ? 'Publish recipe' : 'Publicar receta',
        allDiff: isEn ? 'All levels' : 'Todos los niveles',
        easy: isEn ? 'Easy' : 'Fácil',
        medium: 'Media',
        hard: isEn ? 'Hard' : 'Difícil',
        min: isEn ? 'min' : 'min',
        votes: isEn ? 'votes' : 'votos',
        empty: isEn ? 'No recipes yet. Publish the first one!' : 'Aún no hay recetas. ¡Publica la primera!',
        loginToVote: isEn ? 'Sign in to vote' : 'Entrar para votar',
        edit: isEn ? 'Edit' : 'Editar',
        del: isEn ? 'Delete' : 'Eliminar',
        back: isEn ? 'Back to feed' : 'Volver al feed',
        fTitle: isEn ? 'Recipe title' : 'Título de la receta',
        fDesc: isEn ? 'Short description…' : 'Descripción corta…',
        fIng: isEn ? 'Ingredients (one per line)' : 'Ingredientes (uno por línea)',
        fSteps: isEn ? 'Steps (one per line)' : 'Pasos (uno por línea)',
        fProduct: isEn ? 'Related product (optional name)' : 'Producto relacionado (nombre opcional)',
        fTime: isEn ? 'Prep minutes' : 'Minutos de preparación',
        publish: isEn ? 'Publish' : 'Publicar',
        save: isEn ? 'Save changes' : 'Guardar cambios',
        seeProduct: isEn ? 'See product' : 'Ver producto',
        by: isEn ? 'by' : 'por',
    };
}

async function openRecipesModal() {
    document.getElementById("recipes-modal").classList.remove("hidden");
    renderRecipesFeed();
}

function closeRecipesModal(event) {
    if (event && event.target.id !== "recipes-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("recipes-modal").classList.add("hidden");
}

function difficultyLabel(d) {
    const T = recipesI18nT();
    return { facil: T.easy, media: T.medium, dificil: T.hard }[d] || d;
}

async function renderRecipesFeed() {
    const body = document.getElementById("recipes-body");
    const T = recipesI18nT();
    const isEn = state.lang === 'en';
    body.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.6rem; margin-bottom:0.8rem">
            <h2 style="margin:0">👨‍🍳 ${T.title}</h2>
            <button type="button" id="recipe-new-btn" class="btn btn-sm btn-primary">＋ ${T.newRecipe}</button>
        </div>
        <p style="color:var(--text-secondary); margin-bottom:0.8rem">${T.sub}</p>
        <div style="display:flex; gap:0.6rem; flex-wrap:wrap; margin-bottom:1rem">
            <input type="search" id="recipes-q" class="search-input" placeholder="🔎 ${isEn ? 'Search recipes…' : 'Buscar recetas…'}" value="${escAttr(recipesFilter.q)}" style="max-width:240px">
            <select id="recipes-difficulty" class="lang-picker">
                <option value="">${T.allDiff}</option>
                <option value="facil"${recipesFilter.difficulty === "facil" ? " selected" : ""}>${T.easy}</option>
                <option value="media"${recipesFilter.difficulty === "media" ? " selected" : ""}>${T.medium}</option>
                <option value="dificil"${recipesFilter.difficulty === "dificil" ? " selected" : ""}>${T.hard}</option>
            </select>
            <select id="recipes-sort" class="lang-picker">
                <option value="votes"${recipesFilter.sort === "votes" ? " selected" : ""}>🔥 ${isEn ? 'Most voted' : 'Más votadas'}</option>
                <option value="recent"${recipesFilter.sort === "recent" ? " selected" : ""}>🆕 ${isEn ? 'Recent' : 'Recientes'}</option>
            </select>
        </div>
        <div id="recipes-loading" role="status" aria-live="polite" style="color:var(--text-muted)">${isEn ? 'Loading…' : 'Cargando…'}</div>
        <div id="recipes-list" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:1rem"></div>
        <div id="recipes-pager" style="display:flex; gap:0.5rem; justify-content:center; margin-top:1rem"></div>`;

    document.getElementById("recipe-new-btn").addEventListener("click", () => renderRecipeForm(null));
    const qInput = document.getElementById("recipes-q");
    let debounce;
    qInput.addEventListener("input", () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
            recipesFilter.q = qInput.value.trim();
            recipesFilter.page = 1;
            loadRecipesIntoList();
        }, 350);
    });
    document.getElementById("recipes-difficulty").addEventListener("change", (e) => {
        recipesFilter.difficulty = e.target.value;
        recipesFilter.page = 1;
        loadRecipesIntoList();
    });
    document.getElementById("recipes-sort").addEventListener("change", (e) => {
        recipesFilter.sort = e.target.value;
        recipesFilter.page = 1;
        loadRecipesIntoList();
    });
    await loadRecipesIntoList();
}

async function loadRecipesIntoList() {
    const listEl = document.getElementById("recipes-list");
    const loadingEl = document.getElementById("recipes-loading");
    if (!listEl) return;
    const T = recipesI18nT();
    const isEn = state.lang === 'en';
    loadingEl.classList.remove("hidden");
    listEl.innerHTML = "";
    const params = new URLSearchParams({
        sort: recipesFilter.sort,
        page: String(recipesFilter.page),
        page_size: "12",
    });
    if (recipesFilter.q) params.set("q", recipesFilter.q);
    if (recipesFilter.difficulty) params.set("difficulty", recipesFilter.difficulty);
    let data = { total: 0, items: [] };
    try {
        data = await api(`/recipes?${params.toString()}`);
    } catch (e) { /* vacío */ }
    loadingEl.classList.add("hidden");

    listEl.innerHTML = data.items.map((r) => `
        <div class="guide-card" style="background:var(--bg-page); border:1px solid var(--border-color); border-radius:var(--radius-md); padding:1rem; display:flex; flex-direction:column">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem">
                <span class="tag" style="background:rgba(217,107,67,0.12); color:#d96b43; border:1px solid rgba(217,107,67,0.3)">${difficultyLabel(r.difficulty)}</span>
                ${r.prep_time_min ? `<span style="font-size:0.8rem; color:var(--text-muted)">⏱️ ${r.prep_time_min} ${T.min}</span>` : ""}
            </div>
            <h3 style="margin:0 0 0.3rem; color:var(--color-primary); cursor:pointer" data-recipe-open="${r.id}">${esc(r.title)}</h3>
            ${r.description ? `<p style="font-size:0.86rem; color:var(--text-secondary); margin:0 0 0.5rem">${esc(r.description)}</p>` : ""}
            <div style="font-size:0.78rem; color:var(--text-muted); margin-bottom:0.5rem">${T.by} @${esc(r.author.username)} · ${(r.created_at || "").slice(0, 10)}</div>
            <div style="margin-top:auto; display:flex; align-items:center; gap:0.5rem">
                <button type="button" class="btn btn-sm btn-outline" data-recipe-vote="${r.id}" data-voted="${r.voted ? 1 : 0}" title="${currentUser ? "" : T.loginToVote}">
                    ${r.voted ? "▲" : "△"} ${r.votes}
                </button>
                ${r.mine ? `
                    <button type="button" class="btn btn-sm btn-outline" data-recipe-edit="${r.id}">${T.edit}</button>
                    <button type="button" class="btn btn-sm btn-outline" data-recipe-del="${r.id}" style="color:#d96b43">${T.del}</button>` : ""}
            </div>
        </div>`).join("")
        || `<p style="color:var(--text-muted)">${T.empty}</p>`;

    const totalPages = Math.max(1, Math.ceil(data.total / 12));
    const pager = document.getElementById("recipes-pager");
    pager.innerHTML = totalPages > 1
        ? `<button type="button" class="btn btn-sm btn-outline" id="recipes-prev" ${recipesFilter.page <= 1 ? "disabled" : ""}>←</button>
           <span style="align-self:center; font-size:0.85rem; color:var(--text-muted)">${recipesFilter.page}/${totalPages}</span>
           <button type="button" class="btn btn-sm btn-outline" id="recipes-next" ${recipesFilter.page >= totalPages ? "disabled" : ""}>→</button>`
        : "";
    const prev = document.getElementById("recipes-prev");
    if (prev) prev.addEventListener("click", () => { recipesFilter.page--; loadRecipesIntoList(); });
    const next = document.getElementById("recipes-next");
    if (next) next.addEventListener("click", () => { recipesFilter.page++; loadRecipesIntoList(); });

    bindRecipeCardEvents();
}

function bindRecipeCardEvents() {
    const body = document.getElementById("recipes-body");
    if (!body) return;
    body.querySelectorAll("[data-recipe-open]").forEach((el) => {
        el.addEventListener("click", async () => {
            const r = await api(`/recipes/${el.dataset.recipeOpen}`);
            renderRecipeDetail(r);
        });
    });
    body.querySelectorAll("[data-recipe-vote]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            if (!currentUser) { openAuthModal(); return; }
            const id = btn.dataset.recipeVote;
            const voted = btn.dataset.voted === "1";
            try {
                await apiSend(voted ? "DELETE" : "POST", `/recipes/${id}/vote`);
                await loadRecipesIntoList();
            } catch (e) { /* noop */ }
        });
    });
    body.querySelectorAll("[data-recipe-edit]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const r = await api(`/recipes/${btn.dataset.recipeEdit}`);
            renderRecipeForm(r);
        });
    });
    body.querySelectorAll("[data-recipe-del]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            if (!confirm(state.lang === 'en' ? 'Delete this recipe?' : '¿Eliminar esta receta?')) return;
            try {
                await apiSend("DELETE", `/recipes/${btn.dataset.recipeDel}`);
                await loadRecipesIntoList();
            } catch (e) { /* noop */ }
        });
    });
}

function renderRecipeDetail(r) {
    const body = document.getElementById("recipes-body");
    const T = recipesI18nT();
    body.innerHTML = `
        <button type="button" class="btn btn-sm btn-outline" id="recipe-back-btn">← ${T.back}</button>
        <h2 style="margin-top:0.8rem">${esc(r.title)}</h2>
        <div style="display:flex; gap:0.6rem; flex-wrap:wrap; align-items:center; margin-bottom:0.6rem">
            <span class="tag" style="background:rgba(217,107,67,0.12); color:#d96b43; border:1px solid rgba(217,107,67,0.3)">${difficultyLabel(r.difficulty)}</span>
            ${r.prep_time_min ? `<span class="tag">⏱️ ${r.prep_time_min} ${T.min}</span>` : ""}
            <button type="button" class="btn btn-sm btn-outline" data-recipe-vote="${r.id}" data-voted="${r.voted ? 1 : 0}">${r.voted ? "▲" : "△"} ${r.votes} ${T.votes}</button>
            <span style="font-size:0.8rem; color:var(--text-muted)">${T.by} @${esc(r.author.username)}</span>
        </div>
        ${r.description ? `<p style="line-height:1.55">${esc(r.description)}</p>` : ""}
        ${r.ingredients.length ? `<h4>🧺 ${state.lang === 'en' ? 'Ingredients' : 'Ingredientes'}</h4><ul style="line-height:1.7">${r.ingredients.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>` : ""}
        ${r.steps.length ? `<h4>📋 ${state.lang === 'en' ? 'Steps' : 'Pasos'}</h4><ol style="line-height:1.7">${r.steps.map((s) => `<li>${esc(s)}</li>`).join("")}</ol>` : ""}
        ${r.product_id ? `<button type="button" class="btn btn-sm btn-secondary" data-product-link="${r.product_id}">🫙 ${T.seeProduct}</button>` : ""}`;
    document.getElementById("recipe-back-btn").addEventListener("click", renderRecipesFeed);
    const voteBtn = body.querySelector("[data-recipe-vote]");
    if (voteBtn) voteBtn.addEventListener("click", async () => {
        if (!currentUser) { openAuthModal(); return; }
        const voted = voteBtn.dataset.voted === "1";
        try {
            const updated = await api(`/recipes/${r.id}`);
            void updated;
            if (voted) await apiSend("DELETE", `/recipes/${r.id}/vote`); else await apiSend("POST", `/recipes/${r.id}/vote`);
            const fresh = await api(`/recipes/${r.id}`);
            renderRecipeDetail(fresh);
        } catch (e) { /* noop */ }
    });
    const prodBtn = body.querySelector("[data-product-link]");
    if (prodBtn) prodBtn.addEventListener("click", () => {
        closeRecipesModal();
        openDetail(prodBtn.dataset.productLink);
    });
}

function renderRecipeForm(existing) {
    const body = document.getElementById("recipes-body");
    const T = recipesI18nT();
    const isEn = state.lang === 'en';
    body.innerHTML = `
        <button type="button" class="btn btn-sm btn-outline" id="recipe-back-btn">← ${T.back}</button>
        <form id="recipe-form" style="margin-top:0.9rem; display:flex; flex-direction:column; gap:0.7rem; max-width:560px">
            <input type="text" id="rf-title" class="search-input" required minlength="3" maxlength="200" placeholder="${T.fTitle}" value="${existing ? escAttr(existing.title) : ""}" style="width:100%">
            <textarea id="rf-desc" rows="2" maxlength="4000" placeholder="${T.fDesc}" style="border:1px solid var(--border-color); border-radius:var(--radius-sm); background:var(--bg-page); color:var(--text-color); padding:0.5rem; font-family:inherit">${existing && existing.description ? esc(existing.description) : ""}</textarea>
            <div style="display:flex; gap:0.7rem; flex-wrap:wrap">
                <select id="rf-difficulty" class="lang-picker">
                    <option value="facil"${existing && existing.difficulty === "facil" ? " selected" : ""}>${T.easy}</option>
                    <option value="media"${!existing || existing.difficulty === "media" ? " selected" : ""}>${T.medium}</option>
                    <option value="dificil"${existing && existing.difficulty === "dificil" ? " selected" : ""}>${T.hard}</option>
                </select>
                <input type="number" id="rf-time" min="1" max="10000" placeholder="${T.fTime}" value="${existing && existing.prep_time_min ? existing.prep_time_min : ""}" class="search-input" style="max-width:160px">
                <input type="text" id="rf-product" class="search-input" placeholder="${T.fProduct}" value="" style="max-width:260px" list="rf-products-datalist">
                <datalist id="rf-products-datalist"></datalist>
            </div>
            <label style="font-size:0.82rem; color:var(--text-muted)">${T.fIng}</label>
            <textarea id="rf-ing" rows="4" placeholder="repollo\nsal marina\n...">${existing ? esc(existing.ingredients.join("\n")) : ""}</textarea>
            <label style="font-size:0.82rem; color:var(--text-muted)">${T.fSteps}</label>
            <textarea id="rf-steps" rows="5" placeholder="1. ...\n2. ...">${existing ? esc(existing.steps.join("\n")) : ""}</textarea>
            <p id="rf-error" style="color:#d96b43; font-size:0.83rem; min-height:1rem; margin:0"></p>
            <button type="submit" class="btn btn-primary">${existing ? T.save : T.publish}</button>
        </form>`;
    document.getElementById("recipe-back-btn").addEventListener("click", renderRecipesFeed);

    // Autocompletado de productos con la API de sugerencias.
    const productInput = document.getElementById("rf-product");
    const datalist = document.getElementById("rf-products-datalist");
    productInput.addEventListener("input", async () => {
        const q = productInput.value.trim();
        if (q.length < 2) return;
        try {
            const sug = await api(`/products?q=${encodeURIComponent(q)}&page_size=5&fields=name`);
            datalist.innerHTML = (sug.items || []).map((p) => `<option value="${escAttr(p.name)}">`).join("");
        } catch (e) { /* noop */ }
    });

    document.getElementById("recipe-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const errEl = document.getElementById("rf-error");
        errEl.textContent = "";
        if (!currentUser) { openAuthModal(); return; }
        let productId = existing ? existing.product_id : null;
        const productName = document.getElementById("rf-product").value.trim();
        if (productName) {
            try {
                const found = await api(`/products?q=${encodeURIComponent(productName)}&page_size=1`);
                productId = found.items.length ? found.items[0].id : null;
            } catch (err) { productId = null; }
        }
        const payload = {
            title: document.getElementById("rf-title").value.trim(),
            description: document.getElementById("rf-desc").value.trim() || null,
            ingredients: document.getElementById("rf-ing").value.split("\n").map((s) => s.trim()).filter(Boolean),
            steps: document.getElementById("rf-steps").value.split("\n").map((s) => {
                const parts = s.trim().split(/\s+/);
                if (parts.length > 1 && /^\d+[.:]$/.test(parts[0])) parts.shift();
                return parts.join(" ");
            }).filter(Boolean),
            difficulty: document.getElementById("rf-difficulty").value,
            prep_time_min: Number(document.getElementById("rf-time").value) || null,
            product_id: productId,
        };
        try {
            if (existing) {
                await apiSend("PUT", `/recipes/${existing.id}`, payload);
            } else {
                await apiSend("POST", `/recipes`, payload);
            }
            renderRecipesFeed();
        } catch (err2) {
            errEl.textContent = err2.message;
        }
    });
}

let glossaryTimer = null;
let glossaryOpenedTerm = "";

function openGlossaryModal(opts) {
    opts = opts || {};
    document.getElementById("glossary-modal").classList.remove("hidden");
    if (opts.term) {
        const input = document.getElementById("glossary-search");
        input.value = opts.term;
        glossaryOpenedTerm = opts.term;
    }
    renderGlossary();
}

function closeGlossaryModal(event) {
    if (event && event.target.id !== "glossary-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("glossary-modal").classList.add("hidden");
}

async function renderGlossary() {
    const t = i18n[state.lang] || i18n.es;
    const listEl = document.getElementById("glossary-list");
    const term = document.getElementById("glossary-search").value.trim();
    const q = term || glossaryOpenedTerm || "";
    listEl.innerHTML = `<div class="suggest-label">${esc(t.glossary_search)}</div>`;
    let data = [];
    try {
        data = await api(`/glossary?lang=${state.lang}&limit=300&q=${encodeURIComponent(q)}`);
    } catch (e) {
        listEl.innerHTML = `<p class="glossary-empty">${esc(t.glossary_empty).replace("{q}", esc(q))}</p>`;
        return;
    }
    if (!data.length) {
        listEl.innerHTML = `<p class="glossary-empty">${esc(t.glossary_empty).replace("{q}", esc(q))}</p>`;
        return;
    }
    listEl.innerHTML = data.map((g) => `
        <details class="glossary-entry">
            <summary>
                ${esc(g.term)}
                ${g.related_product ? `<button type="button" class="btn btn-outline btn-sm glossary-link" data-action="glossary-product" data-id="${g.related_product_id}" data-name="${escAttr(g.related_product)}">${esc(t.glossary_related)}</button>` : ""}
            </summary>
            <p>${esc(g.definition)}</p>
        </details>
    `).join("");
}

function glossarySearchInput() {
    clearTimeout(glossaryTimer);
    glossaryTimer = setTimeout(renderGlossary, 180);
}

function openLabelModal(name, dateStr, timeStr, storageStr) {
    document.getElementById("lbl-title").textContent = name;
    document.getElementById("lbl-date").textContent = dateStr;
    document.getElementById("lbl-time").textContent = timeStr;
    document.getElementById("lbl-storage").textContent = storageStr;
    document.getElementById("label-modal").classList.remove("hidden");
}

async function openChartsModal() {
    document.getElementById("charts-modal").classList.remove("hidden");
    try {
        const s = await api("/stats");
        lastStats = s;
        renderKPIs(s);
        renderCharts(s);
    } catch (e) { /* ignore */ }
}

function renderKPIs(s) {
    const kpiEl = document.getElementById("kpi-summary");
    if (!kpiEl) return;
    const ingPct = Math.round((s.products_with_ingredients / s.products) * 100);
    const subPct = Math.round((s.products_with_substrate / s.products) * 100);

    kpiEl.innerHTML = `
        <div class="kpi-card">
            <span class="kpi-val">${ingPct}%</span>
            <span class="kpi-lbl">${state.lang === 'en' ? 'Products with Ingredients' : 'Productos con Ingredientes'}</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-val">${subPct}%</span>
            <span class="kpi-lbl">${state.lang === 'en' ? 'Substrates Mapped' : 'Sustratos Mapeados'}</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-val">${s.uses.toLocaleString()}</span>
            <span class="kpi-lbl">${state.lang === 'en' ? 'Cross Product Links' : 'Vínculos de Uso entre Productos'}</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-val">${s.microbes}</span>
            <span class="kpi-lbl">${state.lang === 'en' ? 'Microbe Species' : 'Especies de Microbios'}</span>
        </div>
    `;
}

function renderCharts(s) {
    if (typeof Chart === "undefined") return;

    Object.values(chartInstances).forEach((c) => c && c.destroy());
    chartInstances = {};

    const tickColor = document.documentElement.classList.contains("dark") ? "#a9b6ad" : "#666";
    const legendLabels = { color: tickColor };

    const contCtx = document.getElementById("chart-continent");
    if (contCtx) {
        chartInstances.continent = new Chart(contCtx, {
            type: "doughnut",
            data: {
                labels: Object.keys(s.by_continent),
                datasets: [{
                    data: Object.values(s.by_continent),
                    backgroundColor: ["#2d5a3f", "#c98836", "#d96b43", "#214e78", "#592e78"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom", labels: legendLabels } }
            }
        });
    }

    const srcCtx = document.getElementById("chart-sources");
    if (srcCtx) {
        chartInstances.sources = new Chart(srcCtx, {
            type: "pie",
            data: {
                labels: Object.keys(s.by_source).map((k) => k.toUpperCase()),
                datasets: [{
                    data: Object.values(s.by_source),
                    backgroundColor: ["#225232", "#8c4217", "#592e78", "#214e78"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom", labels: legendLabels } }
            }
        });
    }

    const catCtx = document.getElementById("chart-categories");
    if (catCtx) {
        const sortedCats = Object.entries(s.by_category).sort((a, b) => b[1] - a[1]);
        chartInstances.categories = new Chart(catCtx, {
            type: "bar",
            data: {
                labels: sortedCats.map((c) => c[0].replace(/_/g, " ")),
                datasets: [{
                    label: state.lang === 'en' ? "Registered Ferments" : "Productos registrados",
                    data: sortedCats.map((c) => c[1]),
                    backgroundColor: "#2d5a3f",
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: tickColor } },
                    y: { ticks: { color: tickColor } }
                }
            }
        });
    }
}

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        document.getElementById("detail").classList.add("hidden");
        document.getElementById("ingredient-modal").classList.add("hidden");
        document.getElementById("shopping-modal").classList.add("hidden");
        document.getElementById("microbes-modal").classList.add("hidden");
        document.getElementById("trouble-modal").classList.add("hidden");
        document.getElementById("label-modal").classList.add("hidden");
        document.getElementById("charts-modal").classList.add("hidden");
        document.getElementById("guide-modal").classList.add("hidden");
        document.getElementById("glossary-modal").classList.add("hidden");
        closeSuggest();
    }
});

const guideBtn = document.getElementById("guide-btn");
if (guideBtn) guideBtn.addEventListener("click", openGuideModal);
const courseBtn = document.getElementById("course-btn");
if (courseBtn) courseBtn.addEventListener("click", openCourseModal);
const podcastBtn = document.getElementById("podcast-btn");
if (podcastBtn) podcastBtn.addEventListener("click", openPodcastModal);
const recipesBtn = document.getElementById("recipes-btn");
if (recipesBtn) recipesBtn.addEventListener("click", openRecipesModal);

// --- Eventos del formulario de autenticación (4.1) ---
document.getElementById("auth-form").addEventListener("submit", (e) => {
    const mode = document.getElementById("auth-switch-btn").dataset.mode;
    if (mode === "register") doRegister(e); else doLogin(e);
});
document.getElementById("auth-switch-btn").addEventListener("click", () => {
    setAuthMode(document.getElementById("auth-switch-btn").dataset.mode);
});

const glossaryBtn = document.getElementById("glossary-btn");
if (glossaryBtn) glossaryBtn.addEventListener("click", () => openGlossaryModal({}));
const glossarySearchInputEl = document.getElementById("glossary-search");
if (glossarySearchInputEl) glossarySearchInputEl.addEventListener("input", glossarySearchInput);

document.getElementById("search-form").addEventListener("submit", (e) => {
    e.preventDefault();
    state.q = document.getElementById("q").value.trim();
    state.category = document.getElementById("category").value;
    state.continent = document.getElementById("continent").value;
    state.country = document.getElementById("country").value;
    state.source = document.getElementById("source").value;
    state.diet = document.getElementById("diet").value;
    state.gi = document.getElementById("gi").checked;
    closeSuggest();
    search(1);
});

const suggestState = { items: [], active: -1 };

function closeSuggest() {
    const box = document.getElementById("suggest-box");
    if (!box) return;
    box.classList.add("hidden");
    box.innerHTML = "";
    suggestState.items = [];
    suggestState.active = -1;
    document.getElementById("q").setAttribute("aria-expanded", "false");
}

function renderSuggest(data) {
    const box = document.getElementById("suggest-box");
    const t = i18n[state.lang] || i18n.es;
    const items = [];
    let html = "";
    if (data.products && data.products.length) {
        html += `<div class="suggest-label">${t.suggest_products}</div>`;
        for (const p of data.products) {
            items.push({ ...p, section: "products" });
            const tags = [p.category, p.country].filter(Boolean)
                .map((x) => `<span class="suggest-tag">${esc(x)}</span>`)
                .join("");
            html += `<button type="button" class="suggest-item" data-suggest-index="${items.length - 1}" role="option">
                <span class="suggest-name">${esc(p.name)}</span>${tags}
            </button>`;
        }
    }
    if (data.ingredients && data.ingredients.length) {
        html += `<div class="suggest-label">${t.suggest_ingredients}</div>`;
        for (const ing of data.ingredients) {
            items.push({ ...ing, section: "ingredients" });
            html += `<button type="button" class="suggest-item" data-suggest-index="${items.length - 1}" role="option">
                <span class="suggest-name">${esc(ing.name)}</span>
                ${ing.category ? `<span class="suggest-tag ing">${esc(ing.category)}</span>` : ""}
            </button>`;
        }
    }
    if (data.glossary && data.glossary.length) {
        html += `<div class="suggest-label">${t.suggest_glossary}</div>`;
        for (const gl of data.glossary) {
            items.push({ ...gl, section: "glossary" });
            html += `<button type="button" class="suggest-item" data-suggest-index="${items.length - 1}" role="option">
                <span class="suggest-name">${esc(gl.name)}</span>
                <span class="suggest-tag gloss">${esc(t.glossary_pronounced)}</span>
            </button>`;
        }
    }
    if (!items.length) {
        html = `<div class="suggest-label">${t.suggest_empty.replace("{q}", esc(document.getElementById("q").value.trim()))}</div>`;
    }
    box.innerHTML = html;
    box.classList.remove("hidden");
    suggestState.items = items;
    document.getElementById("q").setAttribute("aria-expanded", "true");
}

function highlightSuggest() {
    const box = document.getElementById("suggest-box");
    box.querySelectorAll(".suggest-item").forEach((el, i) => {
        el.classList.toggle("active", i === suggestState.active);
        el.setAttribute("aria-selected", i === suggestState.active ? "true" : "false");
    });
}

function applySuggestion(item) {
    closeSuggest();
    if (item.section === "glossary") {
        document.getElementById("q").value = "";
        openGlossaryModal({ term: item.name });
        return;
    }
    const input = document.getElementById("q");
    input.value = item.name;
    state.q = item.name;
    search(1);
}

function onSuggestKeydown(e) {
    const box = document.getElementById("suggest-box");
    if (box.classList.contains("hidden") || !suggestState.items.length) return;
    if (e.key === "ArrowDown") {
        e.preventDefault();
        suggestState.active = (suggestState.active + 1) % suggestState.items.length;
        highlightSuggest();
    } else if (e.key === "ArrowUp") {
        e.preventDefault();
        suggestState.active = (suggestState.active - 1 + suggestState.items.length) % suggestState.items.length;
        highlightSuggest();
    } else if (e.key === "Enter" && suggestState.active >= 0) {
        e.preventDefault();
        applySuggestion(suggestState.items[suggestState.active]);
    }
}

let suggestTimer = null;
const qInput = document.getElementById("q");
qInput.addEventListener("input", () => {
    clearTimeout(suggestTimer);
    const term = qInput.value.trim();
    if (term.length < 2) {
        closeSuggest();
        return;
    }
    suggestTimer = setTimeout(async () => {
        try {
            const data = await api(`/search/suggest?q=${encodeURIComponent(term)}&limit=8`);
            renderSuggest(data);
        } catch (e) {
            closeSuggest();
        }
    }, 180);
});
qInput.addEventListener("keydown", onSuggestKeydown);

document.getElementById("fav-filter-btn").addEventListener("click", () => {
    if (state.onlyFavs) {
        search(1);
    } else {
        renderFavorites();
    }
});

document.getElementById("prev-btn").addEventListener("click", () => search(state.page - 1));
document.getElementById("next-btn").addEventListener("click", () => search(state.page + 1));

document.getElementById("random-btn").addEventListener("click", async () => {
    try {
        const p = await api(`/products/random?lang=${state.lang}`);
        openDetail(p.id);
    } catch (e) { /* ignore */ }
});

const seasonalMoreBtn = document.getElementById("seasonal-more-btn");
if (seasonalMoreBtn) {
    seasonalMoreBtn.addEventListener("click", () => {
        seasonalLimit = 100;
        loadSeasonal(false);
    });
}

// ---- Calculadora de Salmuera y ABV ----

function updateBrineCalculator() {
    const weightEl = document.getElementById("calc-weight");
    const targetEl = document.getElementById("calc-target");
    const resultEl = document.getElementById("calc-result-grams");

    if (!weightEl || !targetEl || !resultEl) return;
    const weight = parseFloat(weightEl.value) || 0;
    const pct = parseFloat(targetEl.value) || 2.5;

    const grams = (weight * (pct / 100)).toFixed(1);
    resultEl.textContent = `${grams.endsWith(".0") ? Math.round(grams) : grams} g`;
}

function updateABVCalculator() {
    const ogEl = document.getElementById("abv-og");
    const fgEl = document.getElementById("abv-fg");
    const resultEl = document.getElementById("abv-result-val");

    if (!ogEl || !fgEl || !resultEl) return;
    const og = parseFloat(ogEl.value) || 1.050;
    const fg = parseFloat(fgEl.value) || 1.010;

    const abv = Math.max(0, (og - fg) * 131.25).toFixed(2);
    resultEl.textContent = `${abv} %`;
}

function updateSaltConverter() {
    const valueEl = document.getElementById("salt-conv-value");
    const unitEl = document.getElementById("salt-conv-unit");
    const resultEl = document.getElementById("salt-conv-result");

    if (!valueEl || !unitEl || !resultEl) return;
    const value = parseFloat(valueEl.value) || 0;
    const unit = unitEl.value;

    let pct, gpl, tsp;
    if (unit === "pct") {
        pct = value;
        gpl = value * 10;
        tsp = gpl / 5;
    } else if (unit === "gl") {
        gpl = value;
        pct = gpl / 10;
        tsp = gpl / 5;
    } else {
        tsp = value;
        gpl = tsp * 5;
        pct = gpl / 10;
    }
    const fmt = (n) => (Math.round(n * 10) / 10).toString();
    resultEl.textContent = `${fmt(gpl)} g/L · ${fmt(pct)}% · ${fmt(tsp)} cdtas/L`;
}

function updateVinegarCalculator() {
    const strengthEl = document.getElementById("vin-strength");
    const targetEl = document.getElementById("vin-target");
    const volumeEl = document.getElementById("vin-volume");
    const resultEl = document.getElementById("vin-result");

    if (!strengthEl || !targetEl || !volumeEl || !resultEl) return;
    const strength = parseFloat(strengthEl.value) || 5;
    const target = parseFloat(targetEl.value) || 4.5;
    const volume = parseFloat(volumeEl.value) || 1;

    if (strength <= 0 || target > strength) {
        resultEl.textContent = "Vinagre insuficiente: usa mayor acidez";
        return;
    }
    const vinegarL = volume * (target / strength);
    const waterL = volume - vinegarL;
    const fmt = (n) => `${(Math.round(n * 100) / 100).toString()} L`;
    resultEl.textContent = `${fmt(vinegarL)} vinagre + ${fmt(Math.max(0, waterL))} agua`;
}

function updateAltitudeCalculator() {
    const metersEl = document.getElementById("alt-meters");
    const baseEl = document.getElementById("alt-base");
    const resultEl = document.getElementById("alt-result");

    if (!metersEl || !baseEl || !resultEl) return;
    const meters = parseFloat(metersEl.value) || 0;
    const base = parseFloat(baseEl.value) || 0;

    const extra = meters > 2745 ? 20 : meters > 1830 ? 15 : meters > 915 ? 10 : meters > 305 ? 5 : 0;
    const adjusted = base + extra;
    resultEl.textContent = `${adjusted} min`;
}

function updatePHCalculator() {
    const initEl = document.getElementById("ph-initial");
    const daysEl = document.getElementById("ph-days");
    const tempEl = document.getElementById("ph-temp");
    const resultEl = document.getElementById("ph-result");

    if (!initEl || !daysEl || !tempEl || !resultEl) return;
    const initial = parseFloat(initEl.value) || 6.5;
    const days = parseFloat(daysEl.value) || 7;
    const temp = parseFloat(tempEl.value) || 21;

    const tempFactor = Math.pow(2, (temp - 21) / 10);
    const drop = 0.3 * Math.min(days, 10) * tempFactor;
    const ph = Math.max(3.2, initial - drop);
    const safe = ph <= 4.6;
    resultEl.textContent = `${ph.toFixed(1)} · ${safe ? "seguro" : "precaución"}`;
}

document.getElementById("calc-weight").addEventListener("input", updateBrineCalculator);
document.getElementById("calc-target").addEventListener("change", updateBrineCalculator);

document.getElementById("abv-og").addEventListener("input", updateABVCalculator);
document.getElementById("abv-fg").addEventListener("input", updateABVCalculator);

document.getElementById("salt-conv-value").addEventListener("input", updateSaltConverter);
document.getElementById("salt-conv-unit").addEventListener("change", updateSaltConverter);
document.getElementById("vin-strength").addEventListener("input", updateVinegarCalculator);
document.getElementById("vin-target").addEventListener("input", updateVinegarCalculator);
document.getElementById("vin-volume").addEventListener("input", updateVinegarCalculator);
document.getElementById("alt-meters").addEventListener("input", updateAltitudeCalculator);
document.getElementById("alt-base").addEventListener("input", updateAltitudeCalculator);
document.getElementById("ph-initial").addEventListener("input", updatePHCalculator);
document.getElementById("ph-days").addEventListener("input", updatePHCalculator);
document.getElementById("ph-temp").addEventListener("input", updatePHCalculator);

// ---- Temporizadores de Fermentación (F1 / F2) ----

let timers = JSON.parse(localStorage.getItem("pantry_timers") || "[]");

function saveTimers() {
    localStorage.setItem("pantry_timers", JSON.stringify(timers));
}

function renderTimers() {
    const container = document.getElementById("timers-list");
    if (!container) return;
    if (!timers.length) {
        container.innerHTML = `<p style="color:var(--text-muted); font-size:0.9rem; grid-column:1/-1">${state.lang === 'en' ? 'No active jars in fermentation. Add one above to track progress.' : 'No tienes frascos activos en fermentación. Agrega uno arriba para darle seguimiento.'}</p>`;
        return;
    }

    const now = Date.now();
    container.innerHTML = timers.map((t, idx) => {
        const start = t.startDate;
        const tempC = t.tempC || 21;
        const factor = Math.pow(2, (21 - tempC) / 10);
        const effectiveDays = Math.max(1, Math.round(t.days * factor));
        const totalMs = effectiveDays * 86400000;
        const elapsedMs = now - start;
        const remainingMs = totalMs - elapsedMs;

        const remainingDays = Math.max(0, Math.ceil(remainingMs / 86400000));
        const pct = Math.min(100, Math.max(0, Math.round((elapsedMs / totalMs) * 100)));

        const isReady = remainingMs <= 0;
        const startDateStr = new Date(start).toISOString().slice(0, 10);
        const notesHtml = t.notes ? `<div style="font-size:0.82rem; color:var(--color-primary); background:rgba(45,90,63,0.06); padding:0.3rem 0.5rem; border-radius:4px; margin-top:0.3rem">📝 <strong>${state.lang === 'en' ? 'Notes:' : 'Notas:'}</strong> ${esc(t.notes)}</div>` : "";
        const tempHtml = tempC !== 21
            ? `<div style="font-size:0.78rem; color:var(--text-muted); margin-top:0.2rem">🌡️ ${state.lang === 'en' ? `Adjusted to ${tempC}°C (≈ ${effectiveDays} days)` : `Ajustado a ${tempC}°C (≈ ${effectiveDays} días)`}</div>`
            : "";

        return `
            <div class="timer-item-card">
                <div class="timer-item-head">
                    <h4>🫙 ${esc(t.name)}</h4>
                    <div style="display:flex; gap:0.3rem; align-items:center">
                        <button type="button" class="btn btn-outline btn-sm" data-action="label" data-name="${escAttr(t.name)}" data-date="${startDateStr}" data-time="${t.days} días" data-storage="Refrigerado en F1/F2" title="${state.lang === 'en' ? 'Print label' : 'Imprimir etiqueta'}" aria-label="${state.lang === 'en' ? 'Print label' : 'Imprimir etiqueta'}">🏷️</button>
                        <button type="button" class="chip-remove" data-action="remove-timer" data-index="${idx}" title="${state.lang === 'en' ? 'Remove jar' : 'Eliminar frasco'}" aria-label="${state.lang === 'en' ? 'Remove jar' : 'Eliminar frasco'} ${escAttr(t.name)}">&times;</button>
                    </div>
                </div>
                ${notesHtml}
                ${tempHtml}
                <div class="progress-bar-bg" style="margin-top:0.5rem">
                    <div class="progress-bar-fill" style="width: ${pct}%; background-color: ${isReady ? '#2e7d52' : 'var(--color-primary)'}"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:var(--text-secondary)">
                    <span>${pct}% ${state.lang === 'en' ? 'completed' : 'completado'}</span>
                    <span>${isReady ? (state.lang === 'en' ? '🎉 Ready to taste!' : '🎉 ¡Listo para consumir/probar!') : (state.lang === 'en' ? `${remainingDays} day${remainingDays === 1 ? '' : 's'} left` : `Quedan ${remainingDays} día${remainingDays === 1 ? '' : 's'}`)}</span>
                </div>
            </div>
        `;
    }).join("");
}

function addTimer() {
    const nameEl = document.getElementById("timer-name");
    const daysEl = document.getElementById("timer-days");
    const tempEl = document.getElementById("timer-temp");
    const notesEl = document.getElementById("timer-notes");

    const name = nameEl.value.trim();
    const days = parseInt(daysEl.value, 10);
    const tempC = parseFloat(tempEl ? tempEl.value : 21);
    const notes = notesEl ? notesEl.value.trim() : "";

    if (!name || isNaN(days) || days < 1) {
        alert(state.lang === 'en' ? "Please enter a valid jar name and number of days." : "Por favor ingresa un nombre y cantidad de días válidos.");
        return;
    }

    timers.push({
        name,
        days,
        tempC: isNaN(tempC) || tempC <= 0 ? 21 : tempC,
        notes,
        startDate: Date.now()
    });
    saveTimers();
    renderTimers();

    nameEl.value = "";
    if (notesEl) notesEl.value = "";
}

function removeTimer(idx) {
    timers.splice(idx, 1);
    saveTimers();
    renderTimers();
}

document.getElementById("add-timer-btn").addEventListener("click", addTimer);

// ---- Diagnóstico de Problemas (Troubleshooting) ----

function openTroubleModal() {
    document.getElementById("trouble-outcome").classList.add("hidden");
    document.getElementById("trouble-modal").classList.remove("hidden");
}

function closeTroubleModal(event) {
    if (event && event.target.id !== "trouble-modal" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("trouble-modal").classList.add("hidden");
}

function diagnoseTrouble(type) {
    const outcomeEl = document.getElementById("trouble-outcome");
    outcomeEl.classList.remove("hidden", "safe", "warning", "danger");

    if (type === "kahm") {
        outcomeEl.classList.add("warning");
        outcomeEl.innerHTML = state.lang === 'en' ? `
            <h3>⚪ Diagnosis: Kahm Yeast</h3>
            <p><strong>Status:</strong> Harmless but can alter flavor if left to accumulate.</p>
            <p><strong>Explanation:</strong> Wild yeast growing on the surface in the presence of oxygen when acidity is still low.</p>
            <p><strong>Solution:</strong> Gently skim off the white film with a clean, sanitized spoon. Keep all vegetables submerged under brine using a weight.</p>
        ` : `
            <h3>⚪ Diagnóstico: Levadura Kahm (Kahm Yeast)</h3>
            <p><strong>Estado:</strong> Inofensivo pero puede alterar el sabor si se deja acumular.</p>
            <p><strong>Explicación:</strong> Es una levadura salvaje silvestre que crece en la superficie en presencia de oxígeno cuando la acidez aún es baja.</p>
            <p><strong>Solución:</strong> Retira suavemente la película blanca con una cuchara limpia y desinfectada. Asegúrate de submergir todos los vegetales bajo la salmuera usando un peso.</p>
        `;
    } else if (type === "mold") {
        outcomeEl.classList.add("danger");
        outcomeEl.innerHTML = state.lang === 'en' ? `
            <h3>🟢 Diagnosis: Mold</h3>
            <p><strong>Status:</strong> ⚠️ DANGEROUS — Discard batch.</p>
            <p><strong>Explanation:</strong> Mold spores form fuzzy green, black, or blue growths. They produce mycotoxins that penetrate the liquid.</p>
            <p><strong>Recommendation:</strong> For safety, discard the entire jar contents and thoroughly sanitize the jar with boiling water.</p>
        ` : `
            <h3>🟢 Diagnóstico: Moho Hongo (Mold)</h3>
            <p><strong>Estado:</strong> ⚠️ PELIGROSO — Desechar la preparación.</p>
            <p><strong>Explicación:</strong> Las esporas de moho forman estructuras vellosas de color verde, negro o azul. Producen micotoxinas que penetran todo el líquido.</p>
            <p><strong>Recomendación:</strong> Por tu seguridad, desecha todo el contenido del frasco, lava e higieniza profundamente el frasco con agua hirviendo antes de reutilizarlo.</p>
        `;
    } else if (type === "cloudy") {
        outcomeEl.classList.add("safe");
        outcomeEl.innerHTML = state.lang === 'en' ? `
            <h3>🌫️ Diagnosis: Cloudy Brine</h3>
            <p><strong>Status:</strong> ✅ COMPLETELY NORMAL & HEALTHY.</p>
            <p><strong>Explanation:</strong> Milky brine indicates massive multiplication of beneficial lactic acid bacteria (LAB).</p>
            <p><strong>Recommendation:</strong> No action needed, your ferment is progressing perfectly.</p>
        ` : `
            <h3>🌫️ Diagnóstico: Salmuera Turbia</h3>
            <p><strong>Estado:</strong> ✅ COMPLETAMENTE NORMAL Y SALUDABLE.</p>
            <p><strong>Explicación:</strong> El color blanquecino o turbio en el líquido es una señal positiva de multiplicación masiva de bacterias ácido-lácticas (LAB) sanas.</p>
            <p><strong>Recomendación:</strong> No hagas nada, tu fermento avanza perfectamente.</p>
        `;
    } else if (type === "foul") {
        outcomeEl.classList.add("danger");
        outcomeEl.innerHTML = state.lang === 'en' ? `
            <h3>🤢 Diagnosis: Contamination / Foul Odor</h3>
            <p><strong>Status:</strong> ⚠️ DISCARD BATCH.</p>
            <p><strong>Explanation:</strong> Healthy ferments smell sour or tangy. A sewage or rotten smell means putrefactive bacteria multiplied.</p>
            <p><strong>Recommendation:</strong> Discard contents immediately.</p>
        ` : `
            <h3>🤢 Diagnóstico: Contaminación o Putrefacción</h3>
            <p><strong>Estado:</strong> ⚠️ DESECHAR EL FERMENTO.</p>
            <p><strong>Explicación:</strong> Un fermento saludable huele ácido, agrio o encurtido. Si huele a alcantarilla, basura o carne podrida, significa que bacterias putrefactivas se multiplicaron.</p>
            <p><strong>Recomendación:</strong> Desecha el contenido inmediatamente.</p>
        `;
    } else if (type === "soft") {
        outcomeEl.classList.add("warning");
        outcomeEl.innerHTML = state.lang === 'en' ? `
            <h3>🥬 Diagnosis: Soft Vegetables</h3>
            <p><strong>Status:</strong> Edible but low crunch quality.</p>
            <p><strong>Explanation:</strong> Caused by low salt salinity, high room temperature (>24°C), or pectinolytic enzymes.</p>
            <p><strong>Solution:</strong> Maintain room temperature at 18-22°C and ensure at least 2.5% salinity.</p>
        ` : `
            <h3>🥬 Diagnóstico: Vegetales Blandos</h3>
            <p><strong>Estado:</strong> Comestible pero de baja calidad de textura.</p>
            <p><strong>Explicación:</strong> Ocurre por insuficiente concentración de sal, temperatura ambiente muy alta (>24°C) o la acción de enzimas pectinolíticas.</p>
            <p><strong>Solución:</strong> En futuros fermentos, mantén la temperatura entre 18-22°C y asegura al menos 2.5% de salinidad.</p>
        `;
    }
}

document.getElementById("trouble-btn").addEventListener("click", openTroubleModal);

// ---- Enciclopedia de Microbios ----

async function loadMicrobesModal() {
    const listEl = document.getElementById("microbes-list");
    listEl.innerHTML = `<p>${state.lang === 'en' ? 'Loading fermenting microbes list...' : 'Cargando lista de microbios fermentadores...'}</p>`;
    document.getElementById("microbes-modal").classList.remove("hidden");
    try {
        const microbes = await api("/microbes");
        if (!microbes.length) {
            listEl.innerHTML = `<p>${state.lang === 'en' ? 'No microbes registered.' : 'No hay microbios registrados.'}</p>`;
            return;
        }
        listEl.innerHTML = microbes.map((m) => `
            <div class="microbe-badge" data-name="${escAttr(m.name)}">
                <span>🧫 ${esc(m.name)}</span>
                <span style="font-size:0.75rem; opacity:0.7">${state.lang === 'en' ? 'Search' : 'Buscar'}</span>
            </div>
        `).join("");
    } catch (e) {
        listEl.innerHTML = `<p>${state.lang === 'en' ? 'Error loading microbes list.' : 'Error al cargar la lista de microbios.'}</p>`;
    }
}

function searchMicrobe(name) {
    document.getElementById("microbes-modal").classList.add("hidden");
    document.getElementById("q").value = name;
    state.q = name;
    search(1);
}

// ---- Vista Mapa (Leaflet + markercluster) ----

let mapInstance = null;
let mapCluster = null;

function setView(view) {
    state.view = view;
    const listEl = document.getElementById("product-list");
    const mapEl = document.getElementById("map-view");
    const pagEl = document.querySelector(".pagination");
    const listBtn = document.getElementById("view-list-btn");
    const mapBtn = document.getElementById("view-map-btn");
    listEl.classList.toggle("hidden", view === "map");
    if (mapEl) mapEl.classList.toggle("hidden", view !== "map");
    if (pagEl) pagEl.style.display = view === "map" ? "none" : "";
    listBtn.classList.toggle("active", view === "list");
    mapBtn.classList.toggle("active", view === "map");
    if (view === "map") {
        loadMap();
    } else if (mapInstance) {
        mapInstance.invalidateSize();
    }
}

async function loadMap() {
    const t = i18n[state.lang] || i18n.es;
    const mapEl = document.getElementById("map");
    const loadingEl = document.getElementById("map-loading");
    if (!mapEl) return;
    if (typeof L === "undefined") {
        loadingEl.textContent = state.lang === 'en'
            ? "Map library not loaded (CDN blocked)."
            : "La librería de mapas no se cargó (CDN bloqueado).";
        loadingEl.classList.remove("hidden");
        return;
    }
    loadingEl.textContent = t.map_loading;
    loadingEl.classList.remove("hidden");
    let points = [];
    try {
        points = await api(`/products/geo?${buildQuery(1)}&limit=4000`);
    } catch (e) {
        loadingEl.textContent = t.map_empty;
        return;
    }
    loadingEl.classList.add("hidden");

    if (!mapInstance) {
        mapInstance = L.map("map").setView([20, 10], 2);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 18,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(mapInstance);
        mapCluster = L.markerClusterGroup();
        mapInstance.addLayer(mapCluster);
    }

    mapCluster.clearLayers();
    if (!points.length) {
        loadingEl.textContent = t.map_empty;
        loadingEl.classList.remove("hidden");
        return;
    }
    const markers = points.map((p) => {
        const m = L.marker([p.lat, p.lng]);
        m.bindPopup(`
            <strong>${esc(p.name)}</strong><br>
            ${p.category ? `<span class="map-popup-tag">${esc(p.category)}</span> ` : ""}
            ${p.country ? `<span class="map-popup-tag">${esc(p.country)}</span>` : ""}
            <br><button type="button" class="btn btn-sm map-popup-btn" data-map-product="${p.id}">${esc(t.map_detail)}</button>
        `);
        return m;
    });
    mapCluster.addLayers(markers);
    if (mapInstance) setTimeout(() => mapInstance.invalidateSize(), 60);
}

document.getElementById("view-list-btn").addEventListener("click", () => setView("list"));
document.getElementById("view-map-btn").addEventListener("click", () => setView("map"));

document.addEventListener("click", (e) => {
    const mapBtn = e.target.closest("[data-map-product]");
    if (mapBtn) {
        openDetail(Number(mapBtn.dataset.mapProduct));
    }
});

document.getElementById("microbes-btn").addEventListener("click", loadMicrobesModal);

// Exportar / Importar Despensa en JSON
document.getElementById("export-pantry-btn").addEventListener("click", () => {
    const data = {
        pantry,
        favorites: Array.from(favorites),
        timers,
        exported_at: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mi_despensa_conservas_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
});

document.getElementById("import-pantry-btn").addEventListener("click", () => {
    document.getElementById("import-file-input").click();
});

document.getElementById("import-file-input").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
        try {
            const data = JSON.parse(event.target.result);
            if (data.pantry) {
                if (Array.isArray(data.pantry.ingredients)) pantry.ingredients = data.pantry.ingredients;
                if (Array.isArray(data.pantry.products)) pantry.products = data.pantry.products;
                savePantry();
                renderPantry();
            }
            if (Array.isArray(data.favorites)) {
                data.favorites.forEach((id) => favorites.add(id));
                saveFavorites();
            }
            if (Array.isArray(data.timers)) {
                timers = data.timers;
                saveTimers();
                renderTimers();
            }
            alert(state.lang === 'en' ? "Pantry, favorites, and timers imported successfully!" : "¡Despensa, favoritos y temporizadores importados exitosamente!");
        } catch (err) {
            alert(state.lang === 'en' ? "Error reading JSON file." : "Error al leer el archivo JSON.");
        }
    };
    reader.readAsText(file);
});

// ---- Dashboard: Mi Despensa ----

const pantry = {
    ingredients: JSON.parse(localStorage.getItem("pantry_ing") || "[]"),
    products: JSON.parse(localStorage.getItem("pantry_prod") || "[]"),
};

function savePantry() {
    localStorage.setItem("pantry_ing", JSON.stringify(pantry.ingredients));
    localStorage.setItem("pantry_prod", JSON.stringify(pantry.products));
}

function renderChips(list, containerId, onRemove) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = list.map((item, i) => `
        <span class="chip">${esc(item)}
            <button type="button" class="chip-remove" data-index="${i}" title="Quitar" aria-label="${state.lang === 'en' ? 'Remove' : 'Quitar'} ${escAttr(item)}">&times;</button>
        </span>
    `).join("");
    container.querySelectorAll(".chip-remove").forEach((btn) => {
        btn.addEventListener("click", () => onRemove(Number(btn.dataset.index)));
    });
}

function renderPantry() {
    renderChips(pantry.ingredients, "ing-chips", (i) => {
        pantry.ingredients.splice(i, 1);
        savePantry();
        renderPantry();
    });
    renderChips(pantry.products, "prod-chips", (i) => {
        pantry.products.splice(i, 1);
        savePantry();
        renderPantry();
    });
}

function addFromInput(inputId, listKey) {
    const input = document.getElementById(inputId);
    const values = input.value.split(",").map((v) => v.trim()).filter(Boolean);
    if (!values.length) return;
    for (const v of values) {
        const key = v.toLowerCase();
        if (!pantry[listKey].some((x) => x.toLowerCase() === key)) {
            pantry[listKey].push(v);
        }
    }
    input.value = "";
    savePantry();
    renderPantry();
}

document.getElementById("ing-add").addEventListener("click", () => addFromInput("ing-input", "ingredients"));
document.getElementById("prod-add").addEventListener("click", () => addFromInput("prod-input", "products"));

["ing-input", "prod-input"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                if (id === "ing-input") addFromInput("ing-input", "ingredients");
                else addFromInput("prod-input", "products");
            }
        });
    }
});

let missingIngredientsGlobal = [];

async function loadRecommendations() {
    const box = document.getElementById("recommendations");
    box.classList.remove("hidden");
    box.innerHTML = `<p>${state.lang === 'en' ? 'Analyzing your ingredients and recommending recipes...' : 'Analizando tus ingredientes y recomendando recetas...'}</p>`;
    const params = new URLSearchParams();
    if (pantry.ingredients.length) params.set("ingredients", pantry.ingredients.join(","));
    if (pantry.products.length) params.set("products", pantry.products.join(","));
    if (!pantry.ingredients.length && !pantry.products.length) {
        box.innerHTML = `<p style="color:var(--text-muted)">${state.lang === 'en' ? 'Add at least one ingredient or fermented product to your pantry above to get recommendations.' : 'Agrega al menos un ingrediente o fermentado a tu despensa arriba para consultar.'}</p>`;
        return;
    }
    try {
        const data = await api(`/recommendations?${params.toString()}`);
        missingIngredientsGlobal = [];
        data.make.forEach((p) => {
            if (p.missing) missingIngredientsGlobal.push(...p.missing);
        });
        missingIngredientsGlobal = Array.from(new Set(missingIngredientsGlobal));

        const card = (p, extra = "") => {
            const substrateLabel = state.lang === 'en' ? 'Substrate' : 'Sustrato';
            return `
            <li class="product-card rec-card" data-product-id="${p.id}">
                <div>
                    <h3>${esc(p.name)}</h3>
                    <p class="desc">${esc(p.description || "")}</p>
                    <div class="tags">
                        ${p.substrate ? tag(`${substrateLabel}: ${p.substrate}`, "substrate") : ""}
                        ${p.categories.map((c) => tag(c.name)).join("")}
                    </div>
                </div>
                ${extra}
            </li>`;
        };
            
        const shoppingBtnHtml = missingIngredientsGlobal.length ? `
            <div style="margin-bottom:1rem">
                <button type="button" class="btn btn-secondary btn-sm" data-action="show-shopping">
                    🛒 ${state.lang === 'en' ? `View Shopping List (${missingIngredientsGlobal.length} missing ingredients)` : `Ver Lista de Compras recomendada (${missingIngredientsGlobal.length} ingredientes faltantes)`}
                </button>
            </div>` : "";

        const makeHtml = data.make.length ? `
            <div class="rec-group">
                <h3>${state.lang === 'en' ? `You can prepare (${data.make.length} options)` : `Puedes preparar (${data.make.length} opciones)`}</h3>
                ${shoppingBtnHtml}
                <ul class="products-grid">${data.make.map((p) => {
                    const missing = p.missing && p.missing.length
                        ? `<div class="rec-extra">${state.lang === 'en' ? 'Missing:' : 'Te falta:'} ${p.missing.map((m) => tag(m, "missing")).join("")}</div>`
                        : `<div class="rec-extra" style="color:var(--color-primary); font-weight:600">${state.lang === 'en' ? 'You have everything!' : '¡Tienes todo lo esencial!'}</div>`;
                    const matched = p.matched && p.matched.length
                        ? `<div class="rec-extra">${state.lang === 'en' ? 'Matches:' : 'Coincide con:'} ${p.matched.map((m) => tag(m, "ok")).join("")}</div>`
                        : "";
                    return card(p, matched + missing);
                }).join("")}</ul>
            </div>` : (pantry.ingredients.length ? `<p style="color:var(--text-muted)">${state.lang === 'en' ? 'No direct matches with those substrates.' : 'Con esos sustratos no hay coincidencias directas.'}</p>` : "");
            
        const useHtml = data.use.length ? `
            <div class="rec-group">
                <h3>${state.lang === 'en' ? `You can use the fermented products (${data.use.length} options)` : `Puedes usar lo fermentado (${data.use.length} opciones)`}</h3>
                <ul class="products-grid">${data.use.map((p) => card(p, `
                    <div class="rec-extra">${state.lang === 'en' ? 'Uses:' : 'Utiliza:'} ${p.uses_products.map((u) => tag(u, "ok")).join("")}</div>
                `)).join("")}</ul>
            </div>` : (pantry.products.length ? `<p style="color:var(--text-muted)">${state.lang === 'en' ? 'No preparations found using those fermented products.' : 'No encontramos preparaciones que usen esos fermentados.'}</p>` : "");
            
        box.innerHTML = makeHtml + useHtml;
    } catch (e) {
        box.innerHTML = `<p>${state.lang === 'en' ? 'Error loading recommendations.' : 'Error al consultar recomendaciones.'}</p>`;
    }
}

function showShoppingList() {
    const listEl = document.getElementById("shopping-list-items");
    if (!listEl) return;
    listEl.innerHTML = missingIngredientsGlobal.map((item) => `
        <li>
            <span>🛒 ${esc(item)}</span>
            <button type="button" class="btn btn-sm btn-secondary" data-action="add-to-pantry" data-item="${escAttr(item)}">${state.lang === 'en' ? '+ Add to pantry' : '+ Agregar a despensa'}</button>
        </li>
    `).join("");
    document.getElementById("shopping-modal").classList.remove("hidden");
}

function addIngredientToPantry(item) {
    if (!pantry.ingredients.some((x) => x.toLowerCase() === item.toLowerCase())) {
        pantry.ingredients.push(item);
        savePantry();
        renderPantry();
    }
    showShoppingList();
}

document.getElementById("copy-shopping-btn").addEventListener("click", () => {
    const text = missingIngredientsGlobal.map((i) => `- ${i}`).join("\n");
    const header = state.lang === 'en' ? 'Conservas del Mundo shopping list:' : 'Lista de compras Conservas del Mundo:';
    const msg = state.lang === 'en' ? 'List copied to clipboard!' : '¡Lista copiada al portapapeles!';
    navigator.clipboard.writeText(`${header}\n${text}`).then(() => {
        alert(msg);
    });
});

// Dark Mode
function applyTheme(theme) {
    const root = document.documentElement;
    root.classList.toggle("dark", theme === "dark");
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === "dark" ? "#11151a" : "#2d5a3f";
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = theme === "dark" ? "☀️" : "🌙";
    localStorage.setItem("pantry_theme", theme);
}

document.getElementById("theme-toggle").addEventListener("click", () => {
    applyTheme(document.documentElement.classList.contains("dark") ? "light" : "dark");
    const chartsModal = document.getElementById("charts-modal");
    if (chartsModal && !chartsModal.classList.contains("hidden") && lastStats) {
        renderCharts(lastStats);
    }
});

const mqDark = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
if (mqDark && mqDark.addEventListener) {
    mqDark.addEventListener("change", (e) => {
        if (!localStorage.getItem("pantry_theme")) applyTheme(e.matches ? "dark" : "light");
    });
}

// Selector de Idioma (i18n)
function updateLanguageUI() {
    const t = i18n[state.lang] || i18n.es;

    document.documentElement.lang = state.lang;

    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.dataset.i18n;
        if (t[key]) el.innerHTML = t[key];
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
        const key = el.dataset.i18nPlaceholder;
        if (t[key]) el.placeholder = t[key];
    });

    loadStats();
    loadCategories();
    loadCountries();
    loadDiets();
    loadSeasonal();
    loadTimeline();
    loadFlavorMap();
    loadGuides();
    loadCourse();
    loadPodcastTopics();
    renderTimers();
    search(1);
}

document.getElementById("lang-select").value = state.lang;
document.getElementById("lang-select").addEventListener("change", (e) => {
    state.lang = e.target.value;
    localStorage.setItem("pantry_lang", state.lang);
    updateLanguageUI();
});

document.querySelectorAll(".method-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".method-chip").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.method = btn.dataset.method || "";
        search(1);
    });
});

document.getElementById("recommend-btn").addEventListener("click", loadRecommendations);

const semanticToggle = document.getElementById("semantic");
if (semanticToggle) {
    semanticToggle.addEventListener("change", () => {
        state.semantic = semanticToggle.checked;
        search(1);
    });
}

updateFavBadge();
updateBrineCalculator();
updateABVCalculator();
updateSaltConverter();
updateVinegarCalculator();
updateAltitudeCalculator();
updatePHCalculator();
renderTimers();
renderPantry();
loadStats();
loadCategories();
loadCountries();
loadDiets();
loadSeasonal();
loadTimeline();
loadIngredientDatalist();
loadFlavorMap();
loadGuides();
loadCourse();
loadPodcastTopics();
loadSession();
search(1);
