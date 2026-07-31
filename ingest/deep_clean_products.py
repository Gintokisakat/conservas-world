"""
Script de limpieza profunda de datos para Conservas del Mundo (`data/build.db`).
Elimina ruidos comerciales de empaques (pesos, marcas, envases), desinfecta sintaxis,
traduce títulos al español y preserva alias originales.
"""

import sqlite3
import re

def deep_clean():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Analizando {len(products)} productos para limpieza profunda...")

    cleaned_count = 0

    # 1. Reglas de eliminación de marcas comerciales y empaques
    brand_and_packaging_rules = [
        (r"\bBocal\s+\d+g\b", ""),
        (r"\bcart\.\d+x\d+g\b", ""),
        (r"\b\d+g\b", ""),
        (r"\b\d+ml\b", ""),
        (r"\b\d+cl\b", ""),
        (r"\bPNE\b", ""),
        (r"\b\(sans calibre\)\b", ""),
        (r"\bMaille\b", ""),
        (r"\bAmora Croq'Vert\b", ""),
        (r"\bAmora Croq'Mini\b", ""),
        (r"\bBouton d'Or\b", ""),
        (r"\bd'aucy\b", ""),
        (r"\bMon moment\b", ""),
        (r"\bL'Original\b", ""),
        (r"\bPetits Croquants\b", ""),
        (r"\[\d+\]", ""),  # Referencias de wikipedia tipo [41]
    ]

    # 2. Mapeo específico de escrituras extranjeras
    foreign_script_map = {
        "Xinogalo Or Xinogala (Ξινόγαλα)": "Xinogala (Leche agria griega)",
        "Ariani (Αριάνι)": "Ariani (Yogur bebible griego)",
        "Kefiri (Κεφίρι)": "Kéfir griego",
        "Queso Pot (kuzeh) کوزه": "Queso Kuzeh en vasija de barro",
        "Нарязани кисели краставички": "Pepinillos encurtidos en rodajas",
        "ご飯がススム 辛口キムチ 180G": "Kimchi picante tradicional",
        "Jamila رايبي": "Raïbi Jamila (Bebida láctea de granada)",
        "Dayaخوخ": "Melocotón fermentado",
        "Dried Fish From Баренцев": "Pescado seco del Mar de Barents",
        "Μπύρα 330ml": "Cerveza artesanal griega",
        "Бира 5%": "Cerveza búlgaro-eslava 5%",
    }

    # 3. Mapeo de términos de títulos no traducidos (Inglés / Francés / Alemán)
    translation_phrases = [
        (r"\bBasque Pyrenees Mountain Cheeses\b", "Quesos de montaña de los Pirineos Vascos"),
        (r"\bBulgarian yoghurt\b", "Yogur búlgaro"),
        (r"\bChinese pickles\b", "Encurtidos chinos tradicional (Pao cai)"),
        (r"\bColombian Champus\b", "Champús colombiano"),
        (r"\bBantu beer,Kaffir beer\b", "Cerveza Bantú"),
        (r"\bBetteraves rouges en dés\b", "Remolacha roja en cubos"),
        (r"\bChucrut aux 4 charcuteries au Riesling d'Alsace\b", "Chucrut con charcutería y vino Riesling de Alsacia"),
        (r"\bChucrut garnie d'Alsace\b", "Chucrut guarnecido de Alsacia"),
        (r"\bChucrut aux petits lardons & riesling\b", "Chucrut con panceta salteada y vino Riesling"),
        (r"\bVéritable Chucrut d'Alsace\b", "Chucrut auténtico de Alsacia"),
        (r"\bEncurtido de pigs' feet\b", "Encurtido de patas de cerdo"),
        (r"\bCiss'uq,Ciss'ur\b", "Ciss'uq (Plato esquimal de bayas fermentadas)"),
        (r"\bCincalok,Cinkaluc,Bagoong Alamang\b", "Cincalok (Pasta malaya de camarón fermentado)"),
        (r"\bCaprino Fresco\b", "Queso Caprino fresco de cabra"),
        (r"\bCaprino Stagionato\b", "Queso Caprino curado de cabra"),
        (r"\bColatura di alici\b", "Colatura di alici (Salsa de anchoas fermentadas)"),
        (r"\bCashel Blue\b", "Queso azul Cashel"),
        (r"\bCasu martzu\b", "Queso Casu Martzu tradicional"),
        (r"\bAmarone della Valpolicella\b", "Vino Amarone della Valpolicella"),
        (r"\bAppenzeller Käse\b", "Queso Appenzeller suizo"),
        (r"\bBerliner Weisse\b", "Cerveza Berliner Weisse de trigo"),
        (r"\bBleu d'Auvergne\b", "Queso azul Bleu d'Auvergne"),
        (r"\bFourme d'Ambert\b", "Queso azul Fourme d'Ambert"),
        (r"\bPont-l'Évêque\b", "Queso Pont-l'Évêque"),
        (r"\bVacherin Mont-d'Or\b", "Queso Vacherin Mont-d'Or"),
        (r"\bValle D'Aosta Fromadzo\b", "Queso Fromadzo de Valle de Aosta"),
        (r"\bFontina Val D'Aosta\b", "Queso Fontina de Valle de Aosta"),
        (r"\bCarre de l'est\b", "Queso Carré de l'Est"),
    ]

    for pid, orig_name, desc, source in products:
        new_name = orig_name.strip()
        was_modified = False

        # Fix 1: Foreign script map
        if new_name in foreign_script_map:
            new_name = foreign_script_map[new_name]
            was_modified = True
        else:
            # Fix 2: Packaging noise cleanup
            for pat, repl in brand_and_packaging_rules:
                if re.search(pat, new_name, re.IGNORECASE):
                    new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                    was_modified = True

            # Fix 3: Phrase translation rules
            for pat, repl in translation_phrases:
                if re.search(pat, new_name, re.IGNORECASE):
                    new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                    was_modified = True

        # Clean punctuation leftovers like double spaces, trailing hyphen/comma/slashes
        new_name = re.sub(r"\s+", " ", new_name)
        new_name = re.sub(r"^[\s,\-\.\:\;\/\\]+|[\s,\-\.\:\;\/\\]+$", "", new_name).strip()

        if was_modified and new_name != orig_name and len(new_name) > 1:
            # Check UNIQUE constraint collision
            cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (new_name, pid))
            conflict = cursor.fetchone()
            if conflict:
                candidate_name = f"{new_name} ({orig_name})"
                cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (candidate_name, pid))
                if cursor.fetchone():
                    candidate_name = f"{new_name} (#{pid})"
                new_name = candidate_name

            # Guardar alias original
            cursor.execute("SELECT id FROM product_aliases WHERE product_id = ? AND name = ?", (pid, orig_name))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO product_aliases (product_id, name, language) VALUES (?, ?, ?)", (pid, orig_name, "orig"))

            cursor.execute("UPDATE products SET name = ? WHERE id = ?", (new_name, pid))
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
    print(f"\n🎉 Limpieza profunda completada: {cleaned_count} títulos mejorados.")

if __name__ == "__main__":
    deep_clean()
