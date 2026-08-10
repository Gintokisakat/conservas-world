"""
Script de traducción y refinamiento específico para aceitunas partidas y aderezadas.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def translate_broken_olives():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de aceitunas partidas...")

    cleaned_count = 0

    broken_olive_vocab = [
        # Títulos
        (r"\bAceitunas cassées à l'ajo\b", "Aceitunas partidas al ajo"),
        (r"\bAceitunas cassées\b", "Aceitunas partidas"),
        (r"\bcassées à l'ajo\b", "partidas al ajo"),
        (r"\bcassées\b", "partidas"),

        # Descripciones
        (r"\bverde Aceitunas\b", "Aceitunas verdes"),
        (r"\bacidifier\s*:\s*", "acidulante: "),
        (r"\bacidifier\b", "acidulante"),
        (r"\brapeseed aceite\b", "aceite de colza"),
        (r"\brapeseed oil\b", "aceite de colza"),
        (r"\brapeseed\b", "colza"),
        (r"\bsemolina ajo\b", "ajo en sémola"),
        (r"\bherbs de provence\b", "hierbas de Provenza"),
        (r"\bherbes de provence\b", "hierbas de Provenza"),
        (r"\bparsley\b", "perejil"),
        (r"\bimported Aceitunas\b", "aceitunas importadas"),
        (r"\bimported olives\b", "aceitunas importadas"),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in broken_olive_vocab:
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
    print(f"\n🎉 Proceso completado: {cleaned_count} productos de aceitunas partidas actualizados.")

if __name__ == "__main__":
    translate_broken_olives()
