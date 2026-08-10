"""
Script de traducción final para aceitunas de la cuenca del Mediterráneo y variedades de aceitunas.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def clean_mediterranean():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de la cuenca del Mediterráneo...")

    cleaned_count = 0

    med_vocab = [
        # Títulos
        (r"\bAceitunas verdes du bassin méditerranéen\b", "Aceitunas verdes de la cuenca del Mediterráneo"),
        (r"\bdu bassin méditerranéen\b", "de la cuenca del Mediterráneo"),
        (r"\bAceitunas à la Méditerranéenne, deshuesadas\b", "Aceitunas a la mediterránea deshuesadas"),
        (r"\bAceitunas à la Méditerranéenne\b", "Aceitunas a la mediterránea"),

        # Descripciones
        (r"\bvariété\b", "variedad"),
        (r"\bpoivrons\b", "pimientos"),
        (r"\bpeppers\b", "pimientos"),
        (r"\bmélange de plantas aromáticas\b", "mezcla de plantas aromáticas"),
        (r"\baromatic plant blend\b", "mezcla de plantas aromáticas"),
        (r"\bOrigine des Aceitunas\s*:\s*UE/non UE, selon approvisionnements\b", "Origen de las aceitunas: UE / no UE según suministros"),
        (r"\bPrésence éventuelle de noyaux ou fragments de noyaux\b", "Presencia eventual de huesos o fragmentos de hueso"),
        (r"\bAceitunas conditionnées sous atmosphère protectrice\b", "Aceitunas envasadas en atmósfera protectora"),
        (r"\bacidifiant\s*:\s*", "acidulante: "),
        (r"\brosemary\b", "romero"),
        (r"\bthyme\b", "tomillo"),
        (r"\bsavory\b", "ajedrea"),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in med_vocab:
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
    clean_mediterranean()
