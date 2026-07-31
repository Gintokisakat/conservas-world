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

loadStats();
loadCategories();
loadCountries();
search(1);
