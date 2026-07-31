const state = {
    q: "",
    category: "",
    continent: "",
    country: "",
    source: "",
    page: 1,
    pageSize: 20,
    total: 0,
};

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
            <span class="stat-pill"><strong>${s.products}</strong> productos</span>
            <span class="stat-pill"><strong>${s.countries}</strong> países</span>
            <span class="stat-pill"><strong>${s.ingredients}</strong> ingredientes</span>
            <span class="stat-pill"><strong>${s.categories}</strong> categorías</span>
        `;
    } catch (e) {
        document.getElementById("stats").textContent = "Sin conexión con la API";
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
    state.page = page;
    const list = document.getElementById("product-list");
    list.innerHTML = `<li class="empty">Cargando…</li>`;
    try {
        const data = await api(`/products?${buildQuery(page)}`);
        state.total = data.total;
        renderResults(data.items);
        updatePagination();
    } catch (e) {
        list.innerHTML = `<li class="empty">Error al consultar la API</li>`;
    }
}

function renderResults(items) {
    const list = document.getElementById("product-list");
    document.getElementById("count").textContent =
        `${state.total} resultado${state.total === 1 ? "" : "s"}`;
    if (!items.length) {
        list.innerHTML = `<li class="empty">Sin resultados. Prueba con otros filtros.</li>`;
        return;
    }
    list.innerHTML = items.map((p) => `
        <li class="product-card" onclick="openDetail(${p.id})">
            <h3>${esc(p.name)}</h3>
            <p class="desc">${esc(p.description || "")}</p>
            <div class="tags">
                ${p.categories.map((c) => tag(c.name)).join("")}
                ${p.countries.map((c) => tag(c.name, "country")).join("")}
                ${p.source_tag ? tag(p.source_tag, "source") : ""}
            </div>
        </li>
    `).join("");
}

function updatePagination() {
    const pages = Math.max(1, Math.ceil(state.total / state.pageSize));
    document.getElementById("page-info").textContent = `${state.page} / ${pages}`;
    document.getElementById("prev-btn").disabled = state.page <= 1;
    document.getElementById("next-btn").disabled = state.page >= pages;
}

async function openDetail(id) {
    const body = document.getElementById("detail-body");
    body.innerHTML = `<p>Cargando…</p>`;
    document.getElementById("detail").classList.remove("hidden");
    try {
        const p = await api(`/products/${id}`);
        const section = (title, items) =>
            items && items.length ? `
                <div class="detail-section">
                    <h4>${title}</h4>
                    <ul>${items.map((i) => `<li>${esc(i.name || i.title)}</li>`).join("")}</ul>
                </div>` : "";
        const refs = p.references && p.references.length ? `
            <div class="detail-section">
                <h4>Referencias</h4>
                <ul>${p.references.map((r) => `
                    <li class="reference">${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a>` : esc(r.title)}${r.doi ? ` — DOI ${esc(r.doi)}` : ""}</li>
                `).join("")}</ul>
            </div>` : "";
        body.innerHTML = `
            <h2>${esc(p.name)}</h2>
            ${p.description ? `<p>${esc(p.description)}</p>` : ""}
            ${p.method ? `<p class="method">${esc(p.method)}</p>` : ""}
            ${p.fermentation_time ? `<p><strong>Tiempo de fermentación:</strong> ${esc(p.fermentation_time)}</p>` : ""}
            <div class="tags" style="margin-top:.5rem">
                ${p.categories.map((c) => tag(c.name)).join("")}
                ${p.countries.map((c) => tag(c.name, "country")).join("")}
            </div>
            ${section("Alias", p.aliases)}
            ${section("Ingredientes", p.ingredients)}
            ${section("Microbios", p.microbes)}
            ${refs}
        `;
    } catch (e) {
        body.innerHTML = `<p>No se pudo cargar el producto.</p>`;
    }
}

function closeDetail(event) {
    if (event && event.target.id !== "detail") return;
    document.getElementById("detail").classList.add("hidden");
}

document.getElementById("search-form").addEventListener("submit", (e) => {
    e.preventDefault();
    state.q = document.getElementById("q").value.trim();
    state.category = document.getElementById("category").value;
    state.continent = document.getElementById("continent").value;
    state.country = document.getElementById("country").value;
    state.source = document.getElementById("source").value;
    search(1);
});

document.getElementById("prev-btn").addEventListener("click", () => search(state.page - 1));
document.getElementById("next-btn").addEventListener("click", () => search(state.page + 1));

document.getElementById("random-btn").addEventListener("click", async () => {
    try {
        const p = await api("/products/random");
        openDetail(p.id);
    } catch (e) { /* ignore */ }
});

// ---- Dashboard: Mi despensa ----

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
    container.innerHTML = list.map((item, i) => `
        <span class="chip">${esc(item)}
            <button type="button" class="chip-remove" data-index="${i}" title="Quitar">×</button>
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
    document.getElementById(id).addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            if (id === "ing-input") addFromInput("ing-input", "ingredients");
            else addFromInput("prod-input", "products");
        }
    });
});

async function loadRecommendations() {
    const box = document.getElementById("recommendations");
    box.classList.remove("hidden");
    box.innerHTML = `<p>Cargando…</p>`;
    const params = new URLSearchParams();
    if (pantry.ingredients.length) params.set("ingredients", pantry.ingredients.join(","));
    if (pantry.products.length) params.set("products", pantry.products.join(","));
    if (!pantry.ingredients.length && !pantry.products.length) {
        box.innerHTML = `<p>Agregá al menos un ingrediente o fermentado a tu despensa.</p>`;
        return;
    }
    try {
        const data = await api(`/recommendations?${params.toString()}`);
        const card = (p, extra = "") => `
            <li class="product-card rec-card" onclick="openDetail(${p.id})">
                <h3>${esc(p.name)}</h3>
                <p class="desc">${esc(p.description || "")}</p>
                <div class="tags">
                    ${p.substrate ? `<span class="tag substrate">${esc(p.substrate)}</span>` : ""}
                    ${p.categories.map((c) => tag(c.name)).join("")}
                </div>
                ${extra}
            </li>`;
        const makeHtml = data.make.length ? `
            <div class="rec-group">
                <h3>Puedes hacer ${data.make.length}</h3>
                <ul class="product-list">${data.make.map((p) => {
                    const missing = p.missing && p.missing.length
                        ? ` <div class="rec-extra">Te falta: ${p.missing.map((m) => tag(m, "missing")).join("")}</div>`
                        : ` <div class="rec-extra">¡Tenés todo lo esencial!</div>`;
                    const matched = p.matched && p.matched.length
                        ? `<div class="rec-extra">Coincide con: ${p.matched.map((m) => tag(m, "ok")).join("")}</div>`
                        : "";
                    return card(p, matched + missing);
                }).join("")}</ul>
            </div>` : (pantry.ingredients.length ? `<p class="rec-empty">Con esos sustratos no hay coincidencias directas.</p>` : "");
        const useHtml = data.use.length ? `
            <div class="rec-group">
                <h3>Puedes usar con lo fermentado ${data.use.length}</h3>
                <ul class="product-list">${data.use.map((p) => card(p, `
                    <div class="rec-extra">Usa: ${p.uses_products.map((u) => tag(u, "ok")).join("")}</div>
                `)).join("")}</ul>
            </div>` : (pantry.products.length ? `<p class="rec-empty">No encontramos preparaciones que usen esos fermentados.</p>` : "");
        box.innerHTML = makeHtml + useHtml;
    } catch (e) {
        box.innerHTML = `<p>Error al consultar recomendaciones.</p>`;
    }
}

document.getElementById("recommend-btn").addEventListener("click", loadRecommendations);

renderPantry();

loadStats();
loadCategories();
loadCountries();
search(1);
