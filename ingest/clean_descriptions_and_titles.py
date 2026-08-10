"""
Script de limpieza de descripciones, formato de alérgenos y traducción de texto portugués/galego al español.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def clean_descriptions_and_titles():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando descripciones y títulos de {len(products)} productos...")

    cleaned_count = 0

    # Diccionario de vocabulario portugués/galego en ingredientes
    pt_dict = [
        (r"\bLeite desnatado\b", "Leche desnatada"),
        (r"\bLeite de\b", "Leche de"),
        (r"\bLeite\b", "Leche"),
        (r"\bproteínas do leite\b", "proteínas de la leche"),
        (r"\bmorango\b", "fresa"),
        (r"\bamido de milho\b", "almidón de maíz"),
        (r"\bconcentrado de cenoura\b", "concentrado de zanahoria"),
        (r"\bsumo concentrado de limão\b", "zumo concentrado de limón"),
        (r"\bfermentos láticos\b", "fermentos lácticos"),
        (r"\bágua\b", "agua"),
        (r"\baçúcar\b", "azúcar"),
        (r"\bazeite de oliva\b", "aceite de oliva"),
        (r"\bazeite\b", "aceite de oliva"),
        (r"\bvinagre de vinho\b", "vinagre de vino"),
        (r"\bsal marinho\b", "sal marina"),
        (r"\bsumo de\b", "zumo de"),
        (r"\baromas naturais\b", "aromas naturales"),
        (r"\bedulcorantes\b", "edulcorantes"),
    ]

    for pid, name, desc, _source in products:
        new_name = name.strip()
        new_desc = desc if desc else ""
        modified = False

        # Fix 1: Title cleanup for symbols like '+Proteína Fresa'
        if new_name.startswith("+"):
            new_name = f"Yogur / Leche fermentada {new_name}"
            modified = True

        # Fix 2: Remove allergen Markdown formatting like _Leite_ -> Leite, _mostaza_ -> mostaza
        if "_" in new_name:
            new_name = re.sub(r"_(.*?)_", r"\1", new_name)
            modified = True

        if "_" in new_desc:
            new_desc = re.sub(r"_(.*?)_", r"\1", new_desc)
            modified = True

        # Fix 3: Translate Portuguese ingredient phrases in description
        if new_desc:
            for pat, repl in pt_dict:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

        if modified:
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
    print(f"\n🎉 Limpieza de descripciones completada: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    clean_descriptions_and_titles()
