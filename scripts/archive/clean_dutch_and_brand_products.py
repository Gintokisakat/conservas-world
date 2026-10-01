"""
Script de traducción y refinamiento de productos de la marca AH Terra y descripciones en holandés.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def clean_dutch_and_brand_products():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos...")

    cleaned_count = 0

    # Traducción específica para productos identificados por el usuario
    specific_fixes = {
        "AH Terra Ahumado tempeh": (
            "Tempeh ahumado orgánico",
            "65% haba de soja, agua, harina de arroz, cultivo de hongos fermentadores (Rhizopus)."
        ),
        "AH Terra Tempeh": (
            "Tempeh de soja tradicional",
            "65% haba de soja, agua, harina de arroz, cultivo de hongos fermentadores (Rhizopus)."
        ),
        "AH Terra Biologische Gerookte Tofu": (
            "Tofu ahumado orgánico (AH Terra)",
            "Tofu ahumado con virutas de madera a base de habas de soja orgánicas."
        ),
    }

    # Vocabulario de ingredientes en holandés
    dutch_ingredients = [
        (r"\bsojaboon\b", "haba de soja"),
        (r"\bsojabonen\b", "habas de soja"),
        (r"\brijstebloem\b", "harina de arroz"),
        (r"\brijstbloem\b", "harina de arroz"),
        (r"\btarwebloem\b", "harina de trigo"),
        (r"\bschimmelcultuur\b", "cultivo de hongos fermentadores"),
        (r"\bstartercultuur\b", "cultivo iniciador fermentador"),
        (r"\bzonnebloemolie\b", "aceite de girasol"),
        (r"\bolijfolie\b", "aceite de oliva"),
        (r"\bspecerijen\b", "especias"),
        (r"\bazijn\b", "vinagre"),
        (r"\bgistextract\b", "extracto de levadura"),
        (r"\bgist\b", "levadura"),
        (r"\bsuiker\b", "azúcar"),
        (r"\bzout\b", "sal"),
        (r"\bwater\b", "agua"),
        (r"\bhaver\b", "avena"),
        (r"\bgerst\b", "cebada"),
        (r"\brogge\b", "centeno"),
    ]

    for pid, orig_name, desc, source in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        if orig_name in specific_fixes:
            new_name, new_desc = specific_fixes[orig_name]
            modified = True
        else:
            # Clean AH / AH Terra brand prefix noise from title
            if new_name.startswith("AH Terra "):
                new_name = new_name.replace("AH Terra ", "").strip()
                modified = True
            elif new_name.startswith("AH "):
                new_name = new_name.replace("AH ", "").strip()
                modified = True

            if new_desc:
                for pat, repl in dutch_ingredients:
                    if re.search(pat, new_desc, re.IGNORECASE):
                        new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE).strip()
                        modified = True

        new_name = re.sub(r"\s+", " ", new_name).strip()

        if modified and new_name != orig_name and len(new_name) > 1:
            cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (new_name, pid))
            conflict = cursor.fetchone()
            if conflict:
                candidate_name = f"{new_name} #{pid}"
                cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (candidate_name, pid))
                if cursor.fetchone():
                    candidate_name = f"{new_name} ({source} #{pid})"
                new_name = candidate_name

            cursor.execute("SELECT id FROM product_aliases WHERE product_id = ? AND name = ?", (pid, orig_name))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO product_aliases (product_id, name, language) VALUES (?, ?, ?)", (pid, orig_name, "nl"))

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
    print(f"\n🎉 Limpieza completada: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    clean_dutch_and_brand_products()
