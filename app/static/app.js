const state = {
    q: "",
    category: "",
    continent: "",
    country: "",
    source: "",
    onlyFavs: false,
    page: 1,
    pageSize: 20,
    total: 0,
    lang: localStorage.getItem("pantry_lang") || "es"
};

// Register Service Worker for PWA / Offline support
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/static/sw.js").catch(() => {});
    });
}

const favorites = new Set(JSON.parse(localStorage.getItem("pantry_favs") || "[]"));

function saveFavorites() {
    localStorage.setItem("pantry_favs", JSON.stringify(Array.from(favorites)));
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

async function api(path) {
    const resp = await fetch(path);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}

function esc(text) {
    const div = document.createElement("div");
    div.textContent = text ?? "";
    return div.innerHTML;
}

function tag(text, cls = "") {
    return `<span class="tag ${cls}">${esc(text)}</span>`;
}

async function loadStats() {
    try {
        const s = await api("/stats");
        document.getElementById("stats").innerHTML = `
            <span class="stat-pill"><strong>${s.products.toLocaleString()}</strong> productos</span>
            <span class="stat-pill"><strong>${s.countries}</strong> países</span>
            <span class="stat-pill"><strong>${s.ingredients}</strong> ingredientes</span>
            <span class="stat-pill"><strong>${s.categories}</strong> categorías</span>
        `;
    } catch (e) {
        document.getElementById("stats").textContent = "API offline";
    }
}

async function loadCategories() {
    try {
        const cats = await api("/categories");
        const select = document.getElementById("category");
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
        for (const c of countries) {
            const opt = document.createElement("option");
            opt.value = c.name;
            opt.textContent = c.name;
            select.appendChild(opt);
        }
    } catch (e) { /* ignore */ }
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
    params.set("page", page);
    params.set("page_size", state.pageSize);
    return params.toString();
}

async function search(page = 1) {
    state.onlyFavs = false;
    document.getElementById("fav-filter-btn").classList.remove("active");
    state.page = page;
    const list = document.getElementById("product-list");
    list.innerHTML = `<li class="empty">Buscando fermentos y conservas...</li>`;
    try {
        const data = await api(`/products?${buildQuery(page)}`);
        state.total = data.total;
        renderResults(data.items);
        updatePagination();
    } catch (e) {
        list.innerHTML = `<li class="empty">Error al conectar con la API. Verifica tu conexión.</li>`;
    }
}

async function renderFavorites() {
    state.onlyFavs = true;
    document.getElementById("fav-filter-btn").classList.add("active");
    const list = document.getElementById("product-list");
    const favIds = Array.from(favorites);
    if (!favIds.length) {
        document.getElementById("count").textContent = "0 favoritos";
        list.innerHTML = `<li class="empty">Aún no tienes productos marcados como favoritos. Haz clic en el corazón ❤️ de cualquier producto para guardarlo aquí.</li>`;
        updatePagination(0);
        return;
    }

    list.innerHTML = `<li class="empty">Cargando tus favoritos...</li>`;
    try {
        const items = await Promise.all(favIds.map((id) => api(`/products/${id}`).catch(() => null)));
        const validItems = items.filter(Boolean);
        state.total = validItems.length;
        document.getElementById("count").textContent = `${validItems.length} favorito${validItems.length === 1 ? "" : "s"}`;
        renderResults(validItems);
        updatePagination(1);
    } catch (e) {
        list.innerHTML = `<li class="empty">Error al cargar tus favoritos.</li>`;
    }
}

function renderResults(items) {
    const list = document.getElementById("product-list");
    document.getElementById("count").textContent =
        `${state.total.toLocaleString()} resultado${state.total === 1 ? "" : "s"}`;
    if (!items.length) {
        list.innerHTML = `<li class="empty">No encontramos fermentos con esos criterios. Prueba ajustando los filtros.</li>`;
        return;
    }
    list.innerHTML = items.map((p) => {
        const isFav = favorites.has(p.id);
        return `
        <li class="product-card" onclick="openDetail(${p.id})">
            <div>
                <div class="card-header-row">
                    <h3>${esc(p.name)}</h3>
                    <button type="button" class="fav-toggle" data-id="${p.id}" onclick="toggleFavorite(${p.id}, event)" title="Marcar como favorito">
                        ${isFav ? "❤️" : "🤍"}
                    </button>
                </div>
                <p class="desc">${esc(p.description || "Sin descripción disponible.")}</p>
            </div>
            <div class="tags">
                ${p.substrate ? tag(p.substrate, "substrate") : ""}
                ${p.categories.map((c) => tag(c.name)).join("")}
                ${p.countries.map((c) => tag(c.name, "country")).join("")}
                ${p.source_tag ? tag(p.source_tag, "source") : ""}
            </div>
        </li>
        `;
    }).join("");
}

function updatePagination(overridePages) {
    const pages = overridePages !== undefined ? overridePages : Math.max(1, Math.ceil(state.total / state.pageSize));
    document.getElementById("page-info").textContent = `Página ${state.page} de ${pages}`;
    document.getElementById("prev-btn").disabled = state.page <= 1 || state.onlyFavs;
    document.getElementById("next-btn").disabled = state.page >= pages || state.onlyFavs;
}

async function openDetail(id) {
    const body = document.getElementById("detail-body");
    body.innerHTML = `<p>Cargando información del fermento...</p>`;
    document.getElementById("detail").classList.remove("hidden");
    try {
        const p = await api(`/products/${id}`);
        const isFav = favorites.has(p.id);
        const section = (title, items) =>
            items && items.length ? `
                <div class="detail-section">
                    <h4>${title}</h4>
                    <ul>${items.map((i) => `<li>${esc(typeof i === "string" ? i : (i.name || i.title))}</li>`).join("")}</ul>
                </div>` : "";
        
        const refs = p.references && p.references.length ? `
            <div class="detail-section">
                <h4>Referencias y Fuentes</h4>
                <ul>${p.references.map((r) => `
                    <li class="reference">${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a>` : esc(r.title)}${r.doi ? ` — DOI: ${esc(r.doi)}` : ""}</li>
                `).join("")}</ul>
            </div>` : "";
            
        body.innerHTML = `
            <div class="card-header-row" style="align-items:center">
                <h2>${esc(p.name)}</h2>
                <div style="display:flex; gap:0.4rem">
                    <button type="button" class="btn btn-outline btn-sm" onclick="openLabelModal('${esc(p.name)}', '${new Date().toISOString().slice(0,10)}', '${esc(p.fermentation_time || '7-14 días')}', '${esc(p.storage_life || 'Refrigerado')}')">
                        🏷️ Imprimir Etiqueta
                    </button>
                    <button type="button" class="btn btn-outline btn-sm" onclick="toggleFavorite(${p.id}); this.textContent = favorites.has(${p.id}) ? '❤️ Guardado' : '🤍 Favorito'">
                        ${isFav ? "❤️ Guardado" : "🤍 Favorito"}
                    </button>
                </div>
            </div>
            ${p.description ? `<p style="font-size:1.05rem; color:var(--text-secondary); margin-bottom:1rem">${esc(p.description)}</p>` : ""}
            ${p.method ? `<p style="background:var(--bg-page); padding:0.8rem; border-radius:var(--radius-sm)"><strong>Método tradicional:</strong> ${esc(p.method)}</p>` : ""}
            ${p.fermentation_time ? `<p><strong>⏱️ Tiempo de fermentación:</strong> ${esc(p.fermentation_time)}</p>` : ""}
            ${p.storage_life ? `<p><strong>🧊 Conservación y almacenamiento:</strong> ${esc(p.storage_life)}</p>` : ""}
            
            <div class="tags" style="margin-top: 0.8rem">
                ${p.substrate ? tag(`Sustrato: ${p.substrate}`, "substrate") : ""}
                ${p.categories.map((c) => tag(c.name)).join("")}
                ${p.countries.map((c) => tag(c.name, "country")).join("")}
            </div>

            <div class="ph-safety-banner">
                <span>🛡️ <strong>Seguridad Alimentaria:</strong> Para fermentación láctica y acética, el pH objetivo de seguridad es <strong>&lt; 4.6</strong> para inhibir esporas de <em>Clostridium botulinum</em>.</span>
            </div>

            ${section("Alias / Nombres locales", p.aliases)}
            ${section("Ingredientes clave", p.ingredients)}
            ${section("Microbios fermentadores", p.microbes)}
            ${section("Utiliza como ingrediente", p.uses)}
            ${section("Es ingrediente de", p.used_by)}
            ${refs}
        `;
    } catch (e) {
        body.innerHTML = `<p>Error al cargar el detalle del producto.</p>`;
    }
}

function closeDetail(event) {
    if (event && event.target.id !== "detail" && !event.target.classList.contains("modal-close")) return;
    document.getElementById("detail").classList.add("hidden");
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

function openLabelModal(name, dateStr, timeStr, storageStr) {
    document.getElementById("lbl-title").textContent = name;
    document.getElementById("lbl-date").textContent = dateStr;
    document.getElementById("lbl-time").textContent = timeStr;
    document.getElementById("lbl-storage").textContent = storageStr;
    document.getElementById("label-modal").classList.remove("hidden");
}

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        document.getElementById("detail").classList.add("hidden");
        document.getElementById("shopping-modal").classList.add("hidden");
        document.getElementById("microbes-modal").classList.add("hidden");
        document.getElementById("trouble-modal").classList.add("hidden");
        document.getElementById("label-modal").classList.add("hidden");
    }
});

document.getElementById("search-form").addEventListener("submit", (e) => {
    e.preventDefault();
    state.q = document.getElementById("q").value.trim();
    state.category = document.getElementById("category").value;
    state.continent = document.getElementById("continent").value;
    state.country = document.getElementById("country").value;
    state.source = document.getElementById("source").value;
    search(1);
});

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
        const p = await api("/products/random");
        openDetail(p.id);
    } catch (e) { /* ignore */ }
});

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

document.getElementById("calc-weight").addEventListener("input", updateBrineCalculator);
document.getElementById("calc-target").addEventListener("change", updateBrineCalculator);

document.getElementById("abv-og").addEventListener("input", updateABVCalculator);
document.getElementById("abv-fg").addEventListener("input", updateABVCalculator);

// ---- Temporizadores de Fermentación (F1 / F2) ----

let timers = JSON.parse(localStorage.getItem("pantry_timers") || "[]");

function saveTimers() {
    localStorage.setItem("pantry_timers", JSON.stringify(timers));
}

function renderTimers() {
    const container = document.getElementById("timers-list");
    if (!container) return;
    if (!timers.length) {
        container.innerHTML = `<p style="color:var(--text-muted); font-size:0.9rem; grid-column:1/-1">No tienes frascos activos en fermentación. Agrega uno arriba para darle seguimiento.</p>`;
        return;
    }

    const now = Date.now();
    container.innerHTML = timers.map((t, idx) => {
        const start = t.startDate;
        const totalMs = t.days * 86400000;
        const elapsedMs = now - start;
        const remainingMs = totalMs - elapsedMs;

        const remainingDays = Math.max(0, Math.ceil(remainingMs / 86400000));
        const pct = Math.min(100, Math.max(0, Math.round((elapsedMs / totalMs) * 100)));

        const isReady = remainingMs <= 0;
        const startDateStr = new Date(start).toISOString().slice(0, 10);

        return `
            <div class="timer-item-card">
                <div class="timer-item-head">
                    <h4>🫙 ${esc(t.name)}</h4>
                    <div style="display:flex; gap:0.3rem; align-items:center">
                        <button type="button" class="btn btn-outline btn-sm" onclick="openLabelModal('${esc(t.name)}', '${startDateStr}', '${t.days} días', 'Refrigerado en F1/F2')" title="Imprimir etiqueta">🏷️</button>
                        <button type="button" class="chip-remove" onclick="removeTimer(${idx})" title="Eliminar frasco">&times;</button>
                    </div>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${pct}%; background-color: ${isReady ? '#2e7d52' : 'var(--color-primary)'}"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:var(--text-secondary)">
                    <span>${pct}% completado</span>
                    <span>${isReady ? '🎉 ¡Listo para consumir/probar!' : `Quedan ${remainingDays} día${remainingDays === 1 ? '' : 's'}`}</span>
                </div>
            </div>
        `;
    }).join("");
}

function addTimer() {
    const nameEl = document.getElementById("timer-name");
    const daysEl = document.getElementById("timer-days");

    const name = nameEl.value.trim();
    const days = parseInt(daysEl.value, 10);

    if (!name || isNaN(days) || days < 1) {
        alert("Por favor ingresa un nombre y cantidad de días válidos.");
        return;
    }

    timers.push({
        name,
        days,
        startDate: Date.now()
    });
    saveTimers();
    renderTimers();

    nameEl.value = "";
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
        outcomeEl.innerHTML = `
            <h3>⚪ Diagnóstico: Levadura Kahm (Kahm Yeast)</h3>
            <p><strong>Estado:</strong> Inofensivo pero puede alterar el sabor si se deja acumular.</p>
            <p><strong>Explicación:</strong> Es una levadura salvaje silvestre que crece en la superficie en presencia de oxígeno cuando la acidez aún es baja.</p>
            <p><strong>Solución:</strong> Retira suavemente la película blanca con una cuchara limpia y desinfectada. Asegúrate de submergir todos los vegetales bajo la salmuera usando un peso.</p>
        `;
    } else if (type === "mold") {
        outcomeEl.classList.add("danger");
        outcomeEl.innerHTML = `
            <h3>🟢 Diagnóstico: Moho Hongo (Mold)</h3>
            <p><strong>Estado:</strong> ⚠️ PELIGROSO — Desechar la preparación.</p>
            <p><strong>Explicación:</strong> Las esporas de moho forman estructuras vellosas de color verde, negro o azul. Producen micotoxinas que penetran todo el líquido.</p>
            <p><strong>Recomendación:</strong> Por tu seguridad, desecha todo el contenido del frasco, lava e higieniza profundamente el frasco con agua hirviendo antes de reutilizarlo.</p>
        `;
    } else if (type === "cloudy") {
        outcomeEl.classList.add("safe");
        outcomeEl.innerHTML = `
            <h3>🌫️ Diagnóstico: Salmuera Turbia</h3>
            <p><strong>Estado:</strong> ✅ COMPLETAMENTE NORMAL Y SALUDABLE.</p>
            <p><strong>Explicación:</strong> El color blanquecino o turbio en el líquido es una señal positiva de multiplicación masiva de bacterias ácido-lácticas (LAB) sanas.</p>
            <p><strong>Recomendación:</strong> No hagas nada, tu fermento avanza perfectamente.</p>
        `;
    } else if (type === "foul") {
        outcomeEl.classList.add("danger");
        outcomeEl.innerHTML = `
            <h3>🤢 Diagnóstico: Contaminación o Putrefacción</h3>
            <p><strong>Estado:</strong> ⚠️ DESECHAR EL FERMENTO.</p>
            <p><strong>Explicación:</strong> Un fermento saludable huele ácido, agrio o encurtido. Si huele a alcantarilla, basura o carne podrida, significa que bacterias putrefactivas se multiplicaron.</p>
            <p><strong>Recomendación:</strong> Desecha el contenido inmediatamente.</p>
        `;
    } else if (type === "soft") {
        outcomeEl.classList.add("warning");
        outcomeEl.innerHTML = `
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
    listEl.innerHTML = `<p>Cargando lista de microbios fermentadores...</p>`;
    document.getElementById("microbes-modal").classList.remove("hidden");
    try {
        const microbes = await api("/microbes");
        if (!microbes.length) {
            listEl.innerHTML = `<p>No hay microbios registrados.</p>`;
            return;
        }
        listEl.innerHTML = microbes.map((m) => `
            <div class="microbe-badge" onclick="searchMicrobe('${esc(m.name)}')">
                <span>🧫 ${esc(m.name)}</span>
                <span style="font-size:0.75rem; opacity:0.7">🔍 Buscar</span>
            </div>
        `).join("");
    } catch (e) {
        listEl.innerHTML = `<p>Error al cargar la lista de microbios.</p>`;
    }
}

function searchMicrobe(name) {
    document.getElementById("microbes-modal").classList.add("hidden");
    document.getElementById("q").value = name;
    state.q = name;
    search(1);
}

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
            alert("¡Despensa, favoritos y temporizadores importados exitosamente!");
        } catch (err) {
            alert("Error al leer el archivo JSON.");
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
            <button type="button" class="chip-remove" data-index="${i}" title="Quitar">&times;</button>
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
    box.innerHTML = `<p>Analizando tus ingredientes y recomendando recetas...</p>`;
    const params = new URLSearchParams();
    if (pantry.ingredients.length) params.set("ingredients", pantry.ingredients.join(","));
    if (pantry.products.length) params.set("products", pantry.products.join(","));
    if (!pantry.ingredients.length && !pantry.products.length) {
        box.innerHTML = `<p style="color:var(--text-muted)">Agrega al menos un ingrediente o fermentado a tu despensa arriba para consultar.</p>`;
        return;
    }
    try {
        const data = await api(`/recommendations?${params.toString()}`);
        missingIngredientsGlobal = [];
        data.make.forEach((p) => {
            if (p.missing) missingIngredientsGlobal.push(...p.missing);
        });
        missingIngredientsGlobal = Array.from(new Set(missingIngredientsGlobal));

        const card = (p, extra = "") => `
            <li class="product-card rec-card" onclick="openDetail(${p.id})">
                <div>
                    <h3>${esc(p.name)}</h3>
                    <p class="desc">${esc(p.description || "")}</p>
                    <div class="tags">
                        ${p.substrate ? tag(`Sustrato: ${p.substrate}`, "substrate") : ""}
                        ${p.categories.map((c) => tag(c.name)).join("")}
                    </div>
                </div>
                ${extra}
            </li>`;
            
        const shoppingBtnHtml = missingIngredientsGlobal.length ? `
            <div style="margin-bottom:1rem">
                <button type="button" class="btn btn-secondary btn-sm" onclick="showShoppingList()">
                    🛒 Ver Lista de Compras recomendada (${missingIngredientsGlobal.length} ingredientes faltantes)
                </button>
            </div>` : "";

        const makeHtml = data.make.length ? `
            <div class="rec-group">
                <h3>🍲 Puedes preparar (${data.make.length} opciones)</h3>
                ${shoppingBtnHtml}
                <ul class="products-grid">${data.make.map((p) => {
                    const missing = p.missing && p.missing.length
                        ? `<div class="rec-extra">Te falta: ${p.missing.map((m) => tag(m, "missing")).join("")}</div>`
                        : `<div class="rec-extra" style="color:var(--color-primary); font-weight:600">¡Tienes todo lo esencial!</div>`;
                    const matched = p.matched && p.matched.length
                        ? `<div class="rec-extra">Coincide con: ${p.matched.map((m) => tag(m, "ok")).join("")}</div>`
                        : "";
                    return card(p, matched + missing);
                }).join("")}</ul>
            </div>` : (pantry.ingredients.length ? `<p style="color:var(--text-muted)">Con esos sustratos no hay coincidencias directas.</p>` : "");
            
        const useHtml = data.use.length ? `
            <div class="rec-group">
                <h3>✨ Puedes usar lo fermentado (${data.use.length} opciones)</h3>
                <ul class="products-grid">${data.use.map((p) => card(p, `
                    <div class="rec-extra">Utiliza: ${p.uses_products.map((u) => tag(u, "ok")).join("")}</div>
                `)).join("")}</ul>
            </div>` : (pantry.products.length ? `<p style="color:var(--text-muted)">No encontramos preparaciones que usen esos fermentados.</p>` : "");
            
        box.innerHTML = makeHtml + useHtml;
    } catch (e) {
        box.innerHTML = `<p>Error al consultar recomendaciones.</p>`;
    }
}

function showShoppingList() {
    const listEl = document.getElementById("shopping-list-items");
    if (!listEl) return;
    listEl.innerHTML = missingIngredientsGlobal.map((item) => `
        <li>
            <span>🛒 ${esc(item)}</span>
            <button type="button" class="btn btn-sm btn-secondary" onclick="addIngredientToPantry('${esc(item)}')">+ Agregar a despensa</button>
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
    navigator.clipboard.writeText(`Lista de compras Conservas del Mundo:\n${text}`).then(() => {
        alert("¡Lista copiada al portapapeles!");
    });
});

// Selector de Idioma (i18n)
document.getElementById("lang-select").value = state.lang;
document.getElementById("lang-select").addEventListener("change", (e) => {
    state.lang = e.target.value;
    localStorage.setItem("pantry_lang", state.lang);
});

document.getElementById("recommend-btn").addEventListener("click", loadRecommendations);

updateFavBadge();
updateBrineCalculator();
updateABVCalculator();
renderTimers();
renderPantry();
loadStats();
loadCategories();
loadCountries();
loadIngredientDatalist();
search(1);
