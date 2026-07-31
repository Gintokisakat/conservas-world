"""
Script de traducción de alérgenos (trazas) y eliminación de ruido de escaneo nutricional OCR.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def clean_traces():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos para alérgenos y ruido OCR...")

    cleaned_count = 0

    trace_map = [
        # Correcciones específicas de producto
        (r"\bAceitunas verdes dénoyautés réduites en sal -25%\b", "Aceitunas verdes deshuesadas bajas en sal (-25 %)"),
        (r"\b\(dine\s*:\s*España\)\b", "(origen: España)"),
        (r"\b\(origine\s*:\s*europe\)\b", "(origen: Europa)"),
        (r"\b\(origine\s*:\s*italie\)\b", "(origen: Italia)"),
        (r"\b\(origine\s*:\s*France\)\b", "(origen: Francia)"),

        # Traducciones de frases de trazas y alérgenos
        (r"\bPeut contenir des traces de\b", "Puede contener trazas de"),
        (r"\bTraces éventuelles de\b", "Trazas eventuales de"),
        (r"\bTraces de\b", "Trazas de"),
        (r"\bmay contain traces de\b", "puede contener trazas de"),
        (r"\bmay contain traces\b", "puede contener trazas de"),
        (r"\bfrutas à coque\b", "frutos de cáscara"),
        (r"\bfrutas à coques\b", "frutos de cáscara"),
        (r"\bOEuf\b", "huevo"),
        (r"\boeufs\b", "huevos"),
        (r"\boeuf\b", "huevo"),
        (r"\bcrustacés\b", "crustáceos"),
        (r"\bmollusques\b", "moluscos"),
        (r"\bgraines de sésame\b", "semillas de sésamo"),
        (r"\bsésame\b", "sésamo"),
        (r"\bcéleri\b", "apio"),
        (r"\bCÉLERI\b", "apio"),
        (r"\blupin\b", "altramuz"),
        (r"\balmond\b", "almendra"),
        (r"\balmonds\b", "almendras"),
        (r"\bamandes\b", "almendras"),
        (r"\bpoisson\b", "pescado"),
        (r"\bpoissons\b", "pescado"),
        (r"\bSOJA\b", "soja"),

        # Limpieza de colas de escaneo OCR
        (r"\s*ONG NUTRITIONNELLES\s*:.*$", "."),
        (r"\s*INFORMATIONS\s*:.*$", "."),
        (r"\s*Analyse des Ingredientes\s*:.*$", "."),
        (r"\s*Analyse des.*$", "."),
        (r"\s*Valeurs nutritionnelles pour 100 g\s*:.*$", "."),
        (r"\s*Valeur énergétique\s*:.*$", "."),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in trace_map:
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
    clean_traces()
