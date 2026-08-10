"""
Script de traducción final para acidifiants, rellenos de anchoa, ajo de oso y champiñones.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def clean_acidifiants():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de acidulantes y rellenos...")

    cleaned_count = 0

    acid_vocab = [
        # Títulos
        (r"\bChampignons de Paris à l’Aceite de tournesol\b", "Champiñones de París en aceite de girasol"),
        (r"\bAceitunas verdes à l’ajo des Ours\b", "Aceitunas verdes al ajo de oso"),
        (r"\bAceitunas verdes à la farce d'Anchois\b", "Aceitunas verdes rellenas de anchoa"),
        (r"\bAceitunas au chile d'Espelette\b", "Aceitunas al chile de Espelette"),

        # Descripciones
        (r"\bacidifiants\s*:\s*", "acidulantes: "),
        (r"\bacidifiants\b", "acidulantes"),
        (r"\bACIDIFIANTS\b", "acidulantes"),
        (r"\b et \b", " y "),
        (r"\b ET \b", " y "),
        (r"\bchampignons de Paris grillés et marinés\b", "champiñones de París a la parrilla y marinados"),
        (r"\bchampignons de Paris\b", "champiñones de París"),
        (r"\baroma natural d'ajo\b", "aroma natural de ajo"),
        (r"\bajo haché réhydraté\b", "ajo picado rehidratado"),
        (r"\bajo des ours\b", "ajo de oso"),
        (r"\bPÂTE D'ANCHOIS\b", "pasta de anchoa"),
        (r"\bSTABILISATEUR\b", "estabilizante"),
        (r"\bEXHAUSTEUR DE GOÛT\b", "potenciador del sabor"),
        (r"\bANTIOXYDANT\b", "antioxidante"),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in acid_vocab:
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
    clean_acidifiants()
