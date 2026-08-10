"""
Script de traducción y limpieza de artefactos comerciales en francés (façon grecque, bocal de, olive maroc).
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def translate_greek_olives():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de aceitunas estilo griego y envases...")

    cleaned_count = 0

    greek_vocab = [
        # Títulos
        (r"\bAceitunas noires entières façon grecque bocal de\b", "Aceitunas negras enteras estilo griego en frasco"),
        (r"\bfaçon grecque\b", "estilo griego"),
        (r"\bfaçon\b", "estilo"),
        (r"\bbocal de\b", "en frasco"),
        (r"\bbocal\b", "frasco"),
        (r"\bnoires entières\b", "negras enteras"),

        # Descripciones
        (r"\borigine\s*:\s*olive maroc\b", "origen: aceitunas de Marruecos"),
        (r"\borigine\s*:\s*maroc\b", "origen: Marruecos"),
        (r"\bolive maroc\b", "aceitunas de Marruecos"),
        (r"\bmaroc\b", "Marruecos"),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in greek_vocab:
            if re.search(pat, new_name, re.IGNORECASE):
                new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                modified = True

            if new_desc and re.search(pat, new_desc, re.IGNORECASE):
                new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE).strip()
                modified = True

        new_name = re.sub(r"\s+", " ", new_name).strip()

        if modified:
            if new_name != orig_name:
                cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (new_name, pid))
                if cursor.fetchone():
                    new_name = f"{new_name} (Variedad {pid})"

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
    print(f"\n🎉 Proceso completado: {cleaned_count} productos de aceitunas estilo griego y envases actualizados.")

if __name__ == "__main__":
    translate_greek_olives()
