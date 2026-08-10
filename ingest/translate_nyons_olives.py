"""
Script de traducción y refinamiento específico para aceitunas de Nyons y aceitunas negras al natural.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def translate_nyons():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de aceitunas de Nyons y aceitunas negras...")

    cleaned_count = 0

    nyons_vocab = [
        # Títulos
        (r"\bAceitunas noires de Nyons AOP\b", "Aceitunas negras de Nyons AOP"),
        (r"\bAceitunas noires de Nyons\b", "Aceitunas negras de Nyons"),
        (r"\bAceitunas noires au naturel\b", "Aceitunas negras al natural"),
        (r"\bAceitunas noires\b", "Aceitunas negras"),

        # Descripciones
        (r"\bAceitunas noires au naturel\b", "Aceitunas negras al natural"),
        (r"\bAceitunas noires\b", "Aceitunas negras"),
        (r"\bnoires au naturel\b", "negras al natural"),
        (r"\bau naturel\b", "al natural"),
        (r"\bnoires\b", "negras"),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in nyons_vocab:
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
    print(f"\n🎉 Proceso completado: {cleaned_count} productos de aceitunas de Nyons y negras actualizados.")

if __name__ == "__main__":
    translate_nyons()
