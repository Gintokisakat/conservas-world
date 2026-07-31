"""
Script de traducción profunda de conectores y términos en inglés para dejar el 100% de las descripciones en español.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def translate_all_english_descriptions():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method FROM products")
    products = cursor.fetchall()

    print(f"📦 Aplicando reemplazo masivo de términos en {len(products)} productos...")
    updated_count = 0

    replacements = [
        # Conectores y artículos
        (r"\b and \b", " y "),
        (r"\b or \b", " o "),
        (r"\b with \b", " con "),
        (r"\b from \b", " de "),
        (r"\b in \b", " en "),
        (r"\b at \b", " en "),
        (r"\b by \b", " por "),
        (r"\b of \b", " de "),
        (r"\b to \b", " para "),
        (r"\b for \b", " para "),
        (r"\b the \b", " el "),
        (r"\b The \b", " El "),
        (r"\b a \b", " un "),
        (r"\b an \b", " un "),
        (r"\b It \b", " Es "),
        (r"\b it \b", " "),
        (r"\b This \b", " Este "),
        (r"\b this \b", " este "),
        (r"\b where \b", " donde "),
        (r"\b which \b", " que "),
        (r"\b that \b", " que "),

        # Términos alimentarios y descriptivos
        (r"\bproduct\b", "producto"),
        (r"\bproducts\b", "productos"),
        (r"\bmilk\b", "leche"),
        (r"\brice\b", "arroz"),
        (r"\bbean\b", "haba / frijol"),
        (r"\bbeans\b", "habas / frijoles"),
        (r"\bflavour\b", "sabor"),
        (r"\bflavor\b", "sabor"),
        (r"\bflavors\b", "sabores"),
        (r"\bflavours\b", "sabores"),
        (r"\bblack\b", "negro"),
        (r"\bwhite\b", "blanco"),
        (r"\bred\b", "rojo"),
        (r"\bgreen\b", "verde"),
        (r"\bhot\b", "caliente"),
        (r"\bcold\b", "frío"),
        (r"\bdry\b", "seco"),
        (r"\bwet\b", "húmedo"),
        (r"\braw\b", "crudo"),
        (r"\bfresh\b", "fresco"),
        (r"\bsweet\b", "dulce"),
        (r"\bsalty\b", "salado"),
        (r"\bhigh\b", "alto"),
        (r"\blow\b", "bajo"),
        (r"\bsmall\b", "pequeño"),
        (r"\blarge\b", "grande"),
        (r"\bsoft\b", "suave / blando"),
        (r"\bhard\b", "duro"),
        (r"\bsimilar\b", "similar"),
        (r"\bmixture\b", "mezcla"),
        (r"\bliquor\b", "licor destilado"),
        (r"\bdrink\b", "bebida"),
        (r"\bdrinks\b", "bebidas"),
        (r"\b dish\b", " plato"),
        (r"\bdishes\b", "platos"),
        (r"\b region\b", " región"),
        (r"\bregions\b", "regiones"),
        (r"\b community\b", " comunidad"),
        (r"\btradition\b", "tradición"),
        (r"\b taste\b", " sabor"),
        (r"\b color\b", " color"),
        (r"\b process\b", " proceso"),
        (r"\b method\b", " método"),
        (r"\b preparation\b", " preparación"),
        (r"\b production\b", " producción"),
        (r"\b fermentation\b", " fermentación"),
        (r"\b fermenting\b", " fermentación"),
    ]

    for pid, name, desc, method in products:
        new_desc = desc if desc else ""
        new_method = method if method else ""
        modified = False

        if new_desc:
            for pat, repl in replacements:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

        if new_method:
            for pat, repl in replacements:
                if re.search(pat, new_method, re.IGNORECASE):
                    new_method = re.sub(pat, repl, new_method, flags=re.IGNORECASE)
                    modified = True

        # Clean multiple spaces or duplicate words like "es un(a)" -> "es un"
        if modified:
            new_desc = re.sub(r"es un\(a\)", "es un", new_desc)
            new_desc = re.sub(r"\s+", " ", new_desc).strip()
            cursor.execute("UPDATE products SET description = ?, method = ? WHERE id = ?", (new_desc if new_desc else None, new_method if new_method else None, pid))
            updated_count += 1

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
    print(f"\n🎉 Traducción universal de conectores completada: {updated_count} productos actualizados.")

if __name__ == "__main__":
    translate_all_english_descriptions()
