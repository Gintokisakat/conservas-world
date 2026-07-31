"""
Script de limpieza final de símbolos (#ID) y backslashes en `data/build.db`.
"""

import sqlite3
import re

def clean_symbols():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    cleaned = 0

    for pid, name, desc in products:
        new_name = name
        new_desc = desc if desc else ""
        modified = False

        # Clean escaped backslashes
        if "\\" in new_name:
            new_name = new_name.replace("\\", "").strip()
            modified = True

        if new_desc and "\\" in new_desc:
            new_desc = new_desc.replace("\\", "").strip()
            modified = True

        # Format #1326 into (Variedad 1326)
        if re.search(r"#\d+", new_name):
            new_name = re.sub(r"#(\d+)", r"(Variedad \1)", new_name).strip()
            modified = True

        if modified:
            cursor.execute("UPDATE products SET name = ?, description = ? WHERE id = ?", (new_name, new_desc if new_desc else None, pid))
            cleaned += 1

    conn.commit()

    # Reconstruir FTS5
    cursor.execute("DROP TABLE IF EXISTS products_fts;")
    cursor.execute("CREATE VIRTUAL TABLE products_fts USING fts5(name, description, content=products, content_rowid=id);")
    cursor.execute('INSERT INTO products_fts(products_fts) VALUES("rebuild");')
    conn.commit()
    conn.close()

    print(f"✅ Se limpiaron símbolos y escapes en {cleaned} productos.")

if __name__ == "__main__":
    clean_symbols()
