"""
Script de traducción y refinamiento específico de Tempeh y productos fermentados restantes.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def clean_tempeh_and_remaining():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products WHERE name LIKE '%tempeh%' OR name LIKE '%tempe%' OR description LIKE '%tempeh%' OR description LIKE '%sojabohnen%'")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de tempeh y derivados...")

    cleaned_count = 0

    tempeh_dict = [
        # Títulos
        (r"\bSmoked tempeh\b", "Tempeh ahumado"),
        (r"\bOrganic Tempeh Smoky Bacon\b", "Tempeh ahumado tipo tocino orgánico"),
        (r"\bChickpea and sunflower seed tempeh\b", "Tempeh de garbanzo y semillas de girasol"),
        (r"\bOriginal Tempeh\b", "Tempeh original"),
        (r"\bTempeh Frais Fume\b", "Tempeh fresco ahumado"),
        (r"\bTempeh Pois chiches fermentés\b", "Tempeh de garbanzo fermentado"),
        (r"\bTempeh di ceci\b", "Tempeh de garbanzo"),
        (r"\bBio tempeh uzený\b", "Tempeh ahumado orgánico"),
        (r"\bTempeh smażony BIO\b", "Tempeh frito orgánico"),
        (r"\bBio tempeh smoky style\b", "Tempeh ahumado estilo artesanal orgánico"),
        (r"\bOrganic High Protein Tempeh\b", "Tempeh alto en proteína orgánico"),
        (r"\bOrganic Tempeh Original Soy\b", "Tempeh de soja orgánico original"),
        (r"\bSojabohnen-Tempeh mit Bergkräutern\b", "Tempeh de soja con hierbas de montaña"),
        (r"\bBio-Tempeh Bergkräuter\b", "Tempeh orgánico con hierbas de montaña"),

        # Vocabulario de ingredientes en descripciones
        (r"\bsoybeans\b", "habas de soja"),
        (r"\bsoya beans\b", "habas de soja"),
        (r"\bSojabohnen\b", "habas de soja"),
        (r"\bSójové boby\b", "habas de soja"),
        (r"\bWachtelbohnen\b", "alubias / frijoles"),
        (r"\bFèves de SOJA\b", "habas de soja"),
        (r"\bFèves de soja\b", "habas de soja"),
        (r"\brice flour\b", "harina de arroz"),
        (r"\bapple vinegar\b", "vinagre de manzana"),
        (r"\bapple cider vinegar\b", "vinagre de sidra de manzana"),
        (r"\bvinagre de cidre\b", "vinagre de manzana"),
        (r"\baceto di mele\b", "vinagre de manzana"),
        (r"\bstarter cultures\b", "cultivos iniciadores fermentadores"),
        (r"\bRhizopus oligosporus\b", "Rhizopus oligosporus (hongo de fermentación)"),
        (r"\bsmoke\b", "humo"),
        (r"\bfiltered water\b", "agua filtrada"),
        (r"\brhizopus culture\b", "cultivo hongo Rhizopus"),
        (r"\bCHICKPEAS\b", "garbanzos"),
        (r"\bSUNFLOWER SEEDS\b", "semillas de girasol"),
        (r"\bWHITE VINEGAR\b", "vinagre blanco"),
        (r"\bRICE FLOUR\b", "harina de arroz"),
        (r"\bfungal culture\b", "cultivo de hongos"),
        (r"\blait de coco\b", "leche de coco"),
        (r"\bnoix de coco\b", "coco"),
        (r"\bgingembre\b", "jengibre"),
        (r"\bdattes\b", "dátiles"),
        (r"\bjus de citron\b", "zumo de limón"),
        (r"\bherbes\b", "hierbas"),
        (r"\bCurcuma\b", "cúrcuma"),
        (r"\bgomme de guar\b", "goma guar"),
    ]

    for pid, orig_name, desc, source in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in tempeh_dict:
            if re.search(pat, new_name, re.IGNORECASE):
                new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                modified = True

            if new_desc and re.search(pat, new_desc, re.IGNORECASE):
                new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE).strip()
                modified = True

        new_name = re.sub(r"\s+", " ", new_name).strip()

        if modified:
            cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (new_name, pid))
            conflict = cursor.fetchone()
            if conflict:
                candidate_name = f"{new_name} #{pid}"
                cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (candidate_name, pid))
                if cursor.fetchone():
                    candidate_name = f"{new_name} ({source} #{pid})"
                new_name = candidate_name

            cursor.execute("UPDATE products SET name = ?, description = ? WHERE id = ?", (new_name, new_desc if new_desc else None, pid))
            cleaned_count += 1

    conn.commit()

    # Reconstruir FTS5
    print("🔄 Reconstruyendo índice FTS5 (products_fts)...")
    try:
        cursor.execute("DROP TABLE IF EXISTS products_fts;")
        cursor.execute("CREATE VIRTUAL TABLE products_fts USING fts5(name, description, content=products, content_rowid=id);")
        cursor.execute('INSERT INTO products_fts(products_fts) VALUES("rebuild");')
        conn.commit()
        print("✅ Índice FTS5 recreado y reconstruido con éxito.")
    except Exception as e:
        print(f"⚠️ Error FTS: {e}")

    conn.close()
    print(f"\n🎉 Limpieza de tempeh completada: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    clean_tempeh_and_remaining()
