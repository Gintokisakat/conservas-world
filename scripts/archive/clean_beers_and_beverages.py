"""
Script de traducción final para cervezas, bebidas y almidones.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def clean_beers():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos de cervezas, bebidas y almidones...")

    cleaned_count = 0

    beer_vocab = [
        # Títulos
        (r"\bASAHI SUPER DRY\b", "Cerveza Asahi Super Dry"),
        (r"\bBiere bud\b", "Cerveza Budweiser"),
        (r"\bNON-ALCOHOLIC BEER\b", "Cerveza sin alcohol"),
        (r"\bBier Tsingtao\b", "Cerveza Tsingtao"),
        (r"\bCerveza blonde pur malt\b", "Cerveza rubia pura malta"),
        (r"\bBiere blonde sans gluten JADE\b", "Cerveza rubia sin gluten Jade"),
        (r"\bBTE BIERE 5% HEINEKEN\b", "Cerveza Heineken 5%"),
        (r"\bBIRRA MORETTI 33 CL\b", "Cerveza Birra Moretti 33 cl"),
        (r"\bBLE BIERE KARMELIET 8,4%V\b", "Cerveza Tripel Karmeliet 8,4%"),
        (r"\bAlkoholfrei\b", "Cerveza sin alcohol"),
        (r"\bBere blondă pasteurizată\b", "Cerveza rubia pasteurizada"),

        # Descripciones
        (r"\bcebada malts\b", "malta de cebada"),
        (r"\bcebada malt\b", "malta de cebada"),
        (r"\bmalted cebada\b", "malta de cebada"),
        (r"\bmalted oats\b", "avena malteada"),
        (r"\btrigo malt\b", "malta de trigo"),
        (r"\bmaíz starch\b", "almidón de maíz"),
        (r"\barroz starch\b", "almidón de arroz"),
        (r"\btapioca starch\b", "almidón de tapioca"),
        (r"\bprocessed maíz starch\b", "almidón de maíz modificado"),
        (r"\bprocessed tapioca starch\b", "almidón de tapioca modificado"),
        (r"\bhop extracts\b", "extractos de lúpulo"),
        (r"\bhop extract\b", "extracto de lúpulo"),
        (r"\bhop\b", "lúpulo"),
        (r"\bhops\b", "lúpulo"),
        (r"\byeasts\b", "levaduras"),
        (r"\bchestnut flouraigne\b", "harina de castaña"),
        (r"\btorrefied trigo\b", "trigo tostado"),
        (r"\bcandi azúcar\b", "azúcar candi"),
    ]

    for pid, orig_name, desc in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in beer_vocab:
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
    clean_beers()
