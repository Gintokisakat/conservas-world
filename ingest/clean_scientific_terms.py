"""
Script de pulido final para términos científicos y descripciones de FermDB.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def clean_scientific():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method FROM products")
    products = cursor.fetchall()

    print(f"📦 Puliendo vocabulario técnico en {len(products)} productos...")
    updated_count = 0

    scientific_map = [
        (r"\bhaba de soja plato\b", "plato a base de habas de soja"),
        (r"\bhaba de soja seeds\b", "semillas de haba de soja"),
        (r"\bcocinado habas / frijoles\b", "habas de soja cocinadas"),
        (r"\bfresco leaves\b", "hojas frescas"),
        (r"\bwrapped mezcla\b", "mezcla envuelta"),
        (r"\bwrapped\b", "envuelto"),
        (r"\bplaced above\b", "colocada sobre"),
        (r"\bplaced\b", "colocado"),
        (r"\bfireplace\b", "fogón tradicional"),
        (r"\bdejado un fermentar\b", "dejado a fermentar"),
        (r"\bun period de\b", "un período de"),
        (r"\binvolves\b", "involucra"),
        (r"\bseeds\b", "semillas"),
        (r"\bseed\b", "semilla"),
        (r"\bleaves\b", "hojas"),
        (r"\bleaf\b", "hoja"),
        (r"\bfamily\b", "familia"),
        (r"\bperiod\b", "período"),
        (r"\b then \b", " luego "),
        (r"\b then\b", " luego"),
        (r"\babove\b", "sobre"),
        (r"\bbelow\b", "debajo de"),
        (r"\bunder\b", "bajo"),
    ]

    for pid, _name, desc, method in products:
        new_desc = desc if desc else ""
        new_method = method if method else ""
        modified = False

        if new_desc:
            for pat, repl in scientific_map:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

        if new_method:
            for pat, repl in scientific_map:
                if re.search(pat, new_method, re.IGNORECASE):
                    new_method = re.sub(pat, repl, new_method, flags=re.IGNORECASE)
                    modified = True

        if modified:
            new_desc = re.sub(r"\s+", " ", new_desc).strip()
            cursor.execute("UPDATE products SET description = ?, method = ? WHERE id = ?", (new_desc if new_desc else None, new_method if new_method else None, pid))
            updated_count += 1

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
    print(f"\n🎉 Pulido de términos científicos completado: {updated_count} productos actualizados.")

if __name__ == "__main__":
    clean_scientific()
