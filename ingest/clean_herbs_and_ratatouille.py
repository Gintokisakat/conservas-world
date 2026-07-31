"""
Script de traducción final para preparaciones con hierbas, tapenades, bouchées y ratatouille.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def clean_herbs():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos con preparaciones de hierbas...")

    cleaned_count = 0

    herbs_vocab = [
        # Títulos
        (r"\bPepinillos extra finos aigre doux aux 3 herbes\b", "Pepinillos extra finos agridulces a las 3 hierbas"),
        (r"\bBouchées marinées au soja\b", "Bocaditos de soja marinados"),
        (r"\bBouchées marinées au curry\b", "Bocaditos al curry marinados"),
        (r"\bKombucha original bio au thé vert\b", "Kombucha original orgánico de té verde"),
        (r"\bAceitunas aux herbes\b", "Aceitunas a las hierbas"),
        (r"\bSardinas à la tapenade\b", "Sardinas en salsa de tapenade"),
        (r"\bRatatouille cuisinée un la provenzal\b", "Ratatouille cocinada a la provenzal"),

        # Descripciones
        (r"\bextrait d'herbes\b", "extracto de hierbas"),
        (r"\baigre doux\b", "agridulce"),
        (r"\baux 3 herbes\b", "a las 3 hierbas"),
        (r"\bherbes aromatiques\b", "hierbas aromáticas"),
        (r"\bherbes\b", "hierbas"),
        (r"\bau thé vert\b", "al té verde"),
        (r"\bmixed aromatic plants\b", "mezcla de plantas aromáticas"),
        (r"\bmélange d'herbes aromatiques\b", "mezcla de hierbas aromáticas"),
        (r"\bCourgettes, aubergines pré-frites\b", "Calabacines, berenjenas prefritas"),
        (r"\bpoivrons rouges\b", "pimientos rojos"),
        (r"\bpurée de tomate double concentrée\b", "puré de tomate doble concentrado"),
        (r"\bjugo / zumo de limón centré\b", "zumo de limón concentrado"),
        (r"\bTous ces Vegetales sont cultivés en España\.\b", "Todos estos vegetales son cultivados en España."),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in herbs_vocab:
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
    print(f"\n🎉 Proceso completado: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    clean_herbs()
