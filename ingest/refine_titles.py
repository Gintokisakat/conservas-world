"""
Refinamiento de limpieza de títulos para Conservas del Mundo.
Limpia sufijos desambiguados extensos, traduce combinaciones de ingredientes comunes en inglés/francés,
y asegura que los títulos sean limpios y elegantes.
"""

import re
import sqlite3


def refine_titles():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Refinando {len(products)} títulos de productos...")

    refined_count = 0

    # Mapeo de frases y sustituciones directas
    substitutions = [
        (r"\bFermento de Classic Kimchi\s*\(Chilli & Garlic\)", "Kimchi clásico con chile y ajo"),
        (r"\bCabbage & Radish Kimchi\b", "Kimchi de repollo y rábano"),
        (r"\bMiso Riz & Soja\b", "Miso de arroz y soja"),
        (r"\bMiso'Easy Chilli Miso\b", "Pasta Miso picante con chile"),
        (r"\bMiso soup paste ginger & turmeric\b", "Pasta para sopa miso con jengibre y cúrcuma"),
        (r"\bDithmarscher\s+Küsten-Kimchi\b", "Kimchi costero Dithmarscher"),
        (r"\bChucrut d'Alsace Bio Cuisinée\b", "Chucrut orgánico de Alsacia cocinado"),
        (r"\bChucrut d'Alsace Bio\b", "Chucrut orgánico de Alsacia"),
        (r"\bPepinillos français à l'estragon\b", "Pepinillos franceses al estragón"),
        (r"\bCreme fraiche\b", "Crema fresca (Crème fraîche)"),
        (r"\bEgyptian Kishk\b", "Kishk egipcio (Trigo y leche fermentada)"),
        (r"\bFlanders brown ale,Oud Bruin\b", "Cerveza tostada de Flandes (Oud Bruin)"),
        (r"\bFlanders red ale\b", "Cerveza roja de Flandes (Flanders red ale)"),
    ]

    for pid, orig_name, _desc, source in products:
        new_name = orig_name.strip()
        was_modified = False

        # Clean trailing parenthetical junk if it contains 'bocal', 'g', 'aucy', 'Maille', 'Amora'
        if "(" in new_name and any(w in new_name.lower() for w in ["bocal", "aucy", "maille", "amora", "g)"]):
            base_part = new_name.split("(")[0].strip()
            if len(base_part) > 3:
                new_name = base_part
                was_modified = True

        for pat, repl in substitutions:
            if re.search(pat, new_name, re.IGNORECASE):
                new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                was_modified = True

        # Clean double spaces or weird quotes
        new_name = re.sub(r"\s+", " ", new_name)
        new_name = re.sub(r"^[\s,\-\.\:\;\/\\]+|[\s,\-\.\:\;\/\\]+$", "", new_name).strip()

        if was_modified and new_name != orig_name and len(new_name) > 1:
            # Check UNIQUE constraint collision
            cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (new_name, pid))
            conflict = cursor.fetchone()
            if conflict:
                candidate_name = f"{new_name} #{pid}"
                cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (candidate_name, pid))
                if cursor.fetchone():
                    candidate_name = f"{new_name} ({source} #{pid})"
                new_name = candidate_name

            cursor.execute("UPDATE products SET name = ? WHERE id = ?", (new_name, pid))
            refined_count += 1

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
    print(f"\n🎉 Refinamiento completado: {refined_count} títulos refinados.")

if __name__ == "__main__":
    refine_titles()
