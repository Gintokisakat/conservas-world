"""
Script completo de limpieza, traducción y normalización de la base de datos `data/build.db`.
Translates English and French entries into Spanish while preserving original names in aliases.
Rebuilds SQLite FTS5 index.
"""

import sqlite3
import re

def clean_and_translate():
    db_path = "data/build.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos...")

    cleaned_count = 0
    translated_count = 0

    # 1. Mapeo directo de nombres específicos
    specific_fixes = {
        "3175681302440": "Tempeh al Curry en Salmuera",
        "6111126001858": "Yogur / Leche Fermentada",
        "16000431 Fish Thai Sause": "Salsa de Pescado Tailandesa (Fish Sauce)",
        "490G 950G": "Aceitunas Deshuesadas en Salmuera",
        "1664": "Cerveza 1664",
        "1664 Blanc Bière Blanche Sans Alcool": "Cerveza 1664 Blanc Sin Alcohol",
        "3 Monts": "Cerveza 3 Monts Tradicional",
        "Vinegar": "Vinagre",
        "Cheese": "Queso",
        "Cheese curds": "Cuajada de queso",
        "Sardines huile d'olives et piment": "Sardinas en aceite de oliva y chile",
        "Raw garlic and dill Chucrut (Sauerkraut)": "Chucrut con ajo crudo y eneldo",
        "Ruby Beetroot Chucrut (Sauerkraut)": "Chucrut con remolacha roja",
        "Chucrut (Sauerkraut) mild aus Weißkohl": "Chucrut suave de repollo blanco",
        "Chucrut (Sauerkraut) white wine": "Chucrut al vino blanco",
        "Bavarian Chucrut (Sauerkraut)": "Chucrut bávaro",
        "Dill pickles": "Pepinillos al eneldo",
        "Hot sauce": "Salsa picante",
        "Chili sauce": "Salsa de chile",
        "Apple cider vinegar": "Vinagre de sidra de manzana",
        "Wine vinegar": "Vinagre de vino",
    }

    # 2. Reglas de reemplazo de prefijos / ruidos numéricos
    noise_prefixes = [
        (r"^\d{2}CL BIERE\s+", "Cerveza "),
        (r"^\d{2}CL\s+", ""),
        (r"^\d+X\d+CL\s+", "Cerveza "),
        (r"^\d+-\d+-\d+\s+\(\d+\)\d+\s+", ""),
        (r"^\d{4}\s+-\s+", ""),
    ]

    # 3. Reglas de traducción Francés -> Español
    fr_replacements = [
        (r"\bCornichons extra-fins\b", "Pepinillos extra finos", re.IGNORECASE),
        (r"\bCornichons extra fins\b", "Pepinillos extra finos", re.IGNORECASE),
        (r"\bCornichons fins\b", "Pepinillos finos", re.IGNORECASE),
        (r"\bCornichons aigres-doux\b", "Pepinillos agridulces", re.IGNORECASE),
        (r"\bCornichons\b", "Pepinillos", re.IGNORECASE),
        (r"\bConfiture de ([\w\sáéíóúñ]+)", r"Mermelada de \1", re.IGNORECASE),
        (r"\bConfiture d'([\w\sáéíóúñ]+)", r"Mermelada de \1", re.IGNORECASE),
        (r"\bConfiture\b", "Mermelada", re.IGNORECASE),
        (r"\bVinaigre de ([\w\sáéíóúñ]+)", r"Vinagre de \1", re.IGNORECASE),
        (r"\bVinaigre d'([\w\sáéíóúñ]+)", r"Vinagre de \1", re.IGNORECASE),
        (r"\bVinaigre\b", "Vinagre", re.IGNORECASE),
        (r"\bFromage de ([\w\sáéíóúñ]+)", r"Queso de \1", re.IGNORECASE),
        (r"\bFromage d'([\w\sáéíóúñ]+)", r"Queso de \1", re.IGNORECASE),
        (r"\bFromage\b", "Queso", re.IGNORECASE),
        (r"\bMoutarde de ([\w\sáéíóúñ]+)", r"Mostaza de \1", re.IGNORECASE),
        (r"\bMoutarde\b", "Mostaza", re.IGNORECASE),
        (r"\bSauce au ([\w\sáéíóúñ]+)", r"Salsa de \1", re.IGNORECASE),
        (r"\bSauce aux ([\w\sáéíóúñ]+)", r"Salsa de \1", re.IGNORECASE),
        (r"\bSauce d'([\w\sáéíóúñ]+)", r"Salsa de \1", re.IGNORECASE),
        (r"\bSauce de ([\w\sáéíóúñ]+)", r"Salsa de \1", re.IGNORECASE),
        (r"\bHuile d'olive\b", "Aceite de oliva", re.IGNORECASE),
        (r"\bHuile de ([\w\sáéíóúñ]+)", r"Aceite de \1", re.IGNORECASE),
        (r"\bJus de ([\w\sáéíóúñ]+)", r"Jugo de \1", re.IGNORECASE),
        (r"\bBière\b", "Cerveza", re.IGNORECASE),
        (r"\bChoucroute\b", "Chucrut", re.IGNORECASE),
        (r"\bLégumes\b", "Vegetales", re.IGNORECASE),
    ]

    # 4. Reglas de traducción Inglés -> Español
    en_replacements = [
        (r"\b([\w\sáéíóúñ]+)\s+Cheese\b", r"Queso \1", re.IGNORECASE),
        (r"\b([\w\sáéíóúñ]+)\s+Vinegar\b", r"Vinagre \1", re.IGNORECASE),
        (r"\b([\w\sáéíóúñ]+)\s+Sauce\b", r"Salsa \1", re.IGNORECASE),
        (r"\bPickled ([\w\sáéíóúñ]+)", r"Encurtido de \1", re.IGNORECASE),
        (r"\bFermented bean curd\b", "Tofu fermentado (Furu)", re.IGNORECASE),
        (r"\bFermented bean paste\b", "Pasta de soja fermentada", re.IGNORECASE),
        (r"\bFermented Tea\b", "Té fermentado", re.IGNORECASE),
        (r"\bFermented ([\w\sáéíóúñ]+)", r"Fermento de \1", re.IGNORECASE),
        (r"\bSauerkraut\b", "Chucrut (Sauerkraut)", re.IGNORECASE),
        (r"\bSweet pickled silverskin onions\b", "Cebollitas agridulces encurtidas", re.IGNORECASE),
        (r"\bBlue cheese\b", "Queso azul", re.IGNORECASE),
        (r"\bFish sauce\b", "Salsa de pescado", re.IGNORECASE),
        (r"\bSoy sauce\b", "Salsa de soja", re.IGNORECASE),
        (r"\bSour cream\b", "Crema agria", re.IGNORECASE),
    ]

    for pid, orig_name, desc, source in products:
        new_name = orig_name.strip()
        was_modified = False

        # Clean square bracket citations from wikipedia e.g. "Herzegovina "squeaking" cheese[41]" -> "Queso crujiente de Herzegovina"
        new_name = re.sub(r'\[\d+\]', '', new_name).strip()

        # Fix 1: Specific fixes
        if new_name in specific_fixes:
            new_name = specific_fixes[new_name]
            was_modified = True
            cleaned_count += 1
        else:
            # Fix 2: Noise prefixes
            for pat, repl in noise_prefixes:
                if re.search(pat, new_name, re.IGNORECASE):
                    new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                    was_modified = True

            # Fix 3: French replacements
            for pat, repl, flags in fr_replacements:
                if re.search(pat, new_name, flags):
                    new_name = re.sub(pat, repl, new_name, flags=flags).strip()
                    was_modified = True
                    translated_count += 1

            # Fix 4: English replacements
            for pat, repl, flags in en_replacements:
                if re.search(pat, new_name, flags):
                    new_name = re.sub(pat, repl, new_name, flags=flags).strip()
                    was_modified = True
                    translated_count += 1

        if was_modified and new_name != orig_name:
            cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (new_name, pid))
            conflict = cursor.fetchone()
            if conflict:
                candidate_name = f"{new_name} ({orig_name})"
                cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (candidate_name, pid))
                if cursor.fetchone():
                    candidate_name = f"{new_name} ({source} #{pid})"
                new_name = candidate_name

            cursor.execute("SELECT id FROM product_aliases WHERE product_id = ? AND name = ?", (pid, orig_name))
            if not cursor.fetchone():
                lang_code = "fr" if any(w in orig_name.lower() for w in ["confiture", "vinaigre", "cornichons", "bière"]) else "en"
                cursor.execute("INSERT INTO product_aliases (product_id, name, language) VALUES (?, ?, ?)", (pid, orig_name, lang_code))

            cursor.execute("UPDATE products SET name = ? WHERE id = ?", (new_name, pid))

    conn.commit()

    # Reconstruir FTS5
    print("🔄 Reconstruyendo índice FTS5 (products_fts)...")
    try:
        cursor.execute("DROP TABLE IF EXISTS products_fts;")
        cursor.execute("CREATE VIRTUAL TABLE products_fts USING fts5(name, description, content=products, content_rowid=id);")
        cursor.execute('INSERT INTO products_fts(products_fts) VALUES("rebuild");')
        conn.commit()
        print("✅ Índice FTS5 reconstruido exitosamente.")
    except Exception as e:
        print(f"⚠️ Error al actualizar FTS: {e}")

    conn.close()

    print("\n🎉 Proceso completado exitosamente.")

if __name__ == "__main__":
    clean_and_translate()
