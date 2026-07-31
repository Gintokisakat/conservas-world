"""
Script de traducción y normalización de conservas de pescado y mariscos.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def translate_seafood_products():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando conservas de pescado en {len(products)} productos...")

    cleaned_count = 0

    seafood_vocab = [
        # Sustituciones exactas de títulos
        (r"\bANCHOVY FILLETS A LA PROVENÇALE in Extra Virgin Olive Oil with Garlic & Herbs\b", "Filetes de anchoa a la provenzal en aceite de oliva virgen extra con ajo y hierbas"),
        (r"\bSweet Chilli Smoked Salmon Fillets\b", "Filetes de salmón ahumado con chile dulce"),
        (r"\bSepia Filletes Of Mackerel In Oil\b", "Filetes de caballa en aceite"),
        (r"\bFilets de Sardine\s*\(au Naturel\)\b", "Filetes de sardina al natural"),
        (r"\bFilet de sardine\b", "Filete de sardina"),
        (r"\bSardine à l’huile végétale\b", "Sardinas en aceite vegetal"),
        (r"\bSardine à la tomate et à l'Aceite de oliva\b", "Sardinas en salsa de tomate y aceite de oliva"),
        (r"\bSardine huile tournesol et limón\b", "Sardinas en aceite de girasol y limón"),
        (r"\bSardine huile olive v\.e\. pim d'Espelette\b", "Sardinas en aceite de oliva virgen extra con pimiento de Espelette"),
        (r"\bSARDINE IN ULEI\b", "Sardinas en aceite"),
        (r"\bAnchovy Fillets\b", "Filetes de anchoa"),
        (r"\bAnchovy\b", "Anchoas"),

        # Frases en títulos y descripciones
        (r"\bANCHOVY FILLETS\b", "Filetes de anchoa"),
        (r"\bAnchovy Fillets\b", "Filetes de anchoa"),
        (r"\bTUNA FILLETS\b", "Filetes de atún"),
        (r"\bTuna Fillets\b", "Filetes de atún"),
        (r"\bSARDINE FILLETS\b", "Filetes de sardina"),
        (r"\bSardine Fillets\b", "Filetes de sardina"),
        (r"\bMACKEREL FILLETS\b", "Filetes de caballa"),
        (r"\bMackerel Fillets\b", "Filetes de caballa"),
        (r"\bin Extra Virgin Olive Oil\b", "en aceite de oliva virgen extra"),
        (r"\bin Olive Oil\b", "en aceite de oliva"),
        (r"\bin Sunflower Oil\b", "en aceite de girasol"),
        (r"\bin Brine\b", "en salmuera"),
        (r"\bwith Garlic & Herbs\b", "con ajo y hierbas"),
        (r"\bwith Garlic and Herbs\b", "con ajo y hierbas"),
        (r"\bwith Garlic\b", "con ajo"),
        (r"\bwith Herbs\b", "con hierbas"),
        (r"\bwith Chilli\b", "con chile"),
        (r"\bwith Lemon\b", "con limón"),
        (r"\bA LA PROVENÇALE\b", "a la provenzal"),
        (r"\bà la provençale\b", "a la provenzal"),
    ]

    for pid, orig_name, desc, source in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in seafood_vocab:
            if re.search(pat, new_name, re.IGNORECASE):
                new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                modified = True

            if new_desc and re.search(pat, new_desc, re.IGNORECASE):
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
                cursor.execute("INSERT INTO product_aliases (product_id, name, language) VALUES (?, ?, ?)", (pid, orig_name, "en"))

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
    print(f"\n🎉 Proceso completado: {cleaned_count} productos de mariscos y conservas actualizados.")

if __name__ == "__main__":
    translate_seafood_products()
