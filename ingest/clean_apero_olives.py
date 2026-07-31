"""
Script de traducción final para aceitunas negras, aperitivos y hierbas provenzales.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def clean_apero_olives():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de aceitunas y aperitivos...")

    cleaned_count = 0

    apero_vocab = [
        # Títulos
        (r"\bAceitunas noires de Nyons AOP\b", "Aceitunas negras de Nyons AOP"),
        (r"\bAceitunas Duo Aux Herbes\b", "Aceitunas dúo a las hierbas"),
        (r"\bAceitunas noires marinées aux hierbas de Provenza\b", "Aceitunas negras marinadas a las hierbas de Provenza"),
        (r"\bAceitunas Apéro à l'ajo\b", "Aceitunas aperitivo al ajo"),
        (r"\bAceitunas un la provenzal\b", "Aceitunas a la provenzal"),
        (r"\bMarinade & basilic hierbas de Provenza\b", "Aceitunas marinadas con albahaca y hierbas de Provenza"),
        (r"\bAceitunas verdes à l'ajo\b", "Aceitunas verdes al ajo"),
        (r"\bSardinas à l'Aceite de oliva et hierbas de Provenza\b", "Sardinas en aceite de oliva y hierbas de Provenza"),

        # Descripciones
        (r"\bnoires au naturel\b", "negras al natural"),
        (r"\bnoires\b", "negras"),
        (r"\bau naturel\b", "al natural"),
        (r"\bpitted Aceitunas verdes\b", "aceitunas verdes deshuesadas"),
        (r"\bpitted\b", "deshuesadas"),
        (r"\bdehydrated\b", "deshidratado"),
        (r"\bcorrector de acidity\b", "corrector de acidez"),
        (r"\bacid citric\b", "ácido cítrico"),
        (r"\bcitric acid\b", "ácido cítrico"),
        (r"\bantioxidant\b", "antioxidante"),
        (r"\bascorbic acid\b", "ácido ascórbico"),
        (r"\bcontains sulphites\b", "contiene sulfitos"),
        (r"\bmoroccan olive\b", "aceitunas marroquíes"),
        (r"\bcandied\b", "confitado"),
        (r"\bbay hoja\b", "hoja de laurel"),
        (r"\bacidifiers\b", "acidulantes"),
        (r"\bbasilic\b", "albahaca"),
        (r"\blaurier\b", "laurel"),
        (r"\borigan\b", "orégano"),
        (r"\bromarin\b", "romero"),
        (r"\bthym\b", "tomillo"),
        (r"\bsarriette\b", "ajedrea"),
        (r"\bmarjolaine\b", "mejorana"),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in apero_vocab:
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
    clean_apero_olives()
