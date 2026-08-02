"""
Script de traducción y perfeccionamiento fluido para Abacha, preparaciones africanas, mandioca y mermeladas.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def clean_african_and_cassava():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de preparaciones africanas y conservas...")

    cleaned_count = 0

    african_vocab = [
        # Abacha y yuca
        (r"\bAfrican ensalada\b", "ensalada africana"),
        (r"\bAfrican ensaladas\b", "ensaladas africanas"),
        (r"\bcassava\b", "yuca (mandioca)"),
        (r"\bsupplementary ingredients\b", "ingredientes adicionales"),
        (r"\bsupplementary\b", "adicionales"),
        (r"\bseasoning\b", "sazonadores"),
        (r"\bseasonings\b", "sazonadores"),
        (r"\badded\b", "añadidos"),
        (r"\bafter que\b", "después de que"),
        (r"\bsuch como\b", "tales como"),

        # Mermeladas y frases en francés
        (r"\bAbricot 65% de fruta\b", "Albaricoque (65% de fruta)"),
        (r"\bAbricot, 65% de frutas\b", "Albaricoque (65% de fruta)"),
        (r"\bMyrtille 65% de fruta\b", "Arándano (65% de fruta)"),
        (r"\bMermelada de Myrtille BIO\b", "Mermelada de arándano orgánica"),
        (r"\bMyrtilles\b", "Arándanos"),
        (r"\bMyrtille\b", "Arándano"),
        (r"\bazúcar de canne\b", "azúcar de caña"),
        (r"\bazúcar de canne\*\b", "azúcar de caña*"),
        (r"\bcanne\b", "caña"),
        (r"\bPréparée avec (\d+)\s*g de frutas pour 100\s*g de produit fini\b", r"Preparada con \1 g de fruta por 100 g de producto terminado"),
        (r"\bPréparée avec (\d+)\s*g de frutas pour 100\s*g\b", r"Preparada con \1 g de fruta por 100 g"),
        (r"\bPréparée avec (\d+)\s*% de frutas pour 100\s*g\b", r"Preparada con \1% de fruta por 100 g"),
        (r"\bPour 100 g de produit fini\s*:\s*préparée avec (\d+) g de frutas\b", r"Por 100 g de producto terminado: preparada con \1 g de fruta"),
        (r"\bproduit fini\b", "producto terminado"),
        (r"\bbiologique\b", "orgánico"),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in african_vocab:
            if re.search(pat, new_name, re.IGNORECASE):
                new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                modified = True

            if new_desc and re.search(pat, new_desc, re.IGNORECASE):
                new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE).strip()
                modified = True

        new_name = re.sub(r"\s+", " ", new_name).strip()
        if new_desc:
            new_desc = re.sub(r"\s+", " ", new_desc).strip()

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
    clean_african_and_cassava()
