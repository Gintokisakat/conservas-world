"""
Script de pulido cero tolerancia con vocabulario botánico, gastronómico y conectores de FermDB.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def zero_tolerance_cleaner():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method, substrate FROM products")
    products = cursor.fetchall()

    print(f"📦 Iniciando pulido cero tolerancia en {len(products)} productos...")

    word_map = [
        (r"\bwhole\b", "entero"),
        (r"\bmustard\b", "mostaza"),
        (r"\bcabbage\b", "repollo"),
        (r"\bonion\b", "cebolla"),
        (r"\bonions\b", "cebollas"),
        (r"\bjars\b", "frascos"),
        (r"\bjar\b", "frasco"),
        (r"\bbroth\b", "caldo"),
        (r"\bseveral\b", "varios"),
        (r"\bmanufacture\b", "elaboración"),
        (r"\bprincipally\b", "principalmente"),
        (r"\bcuisine\b", "cocina tradicional"),
        (r"\bboth\b", "tanto"),
        (r"\bground\b", "molido"),
        (r"\bimmensely\b", "inmensamente"),
        (r"\bvarious\b", "variados"),
        (r"\btype\b", "tipo"),
        (r"\blightly\b", "ligeramente"),
        (r"\brelish\b", "encurtido"),
        (r"\bother\b", "otros"),
        (r"\bcountries\b", "países"),
        (r"\bcountry\b", "país"),
        (r"\bname\b", "nombre"),
        (r"\bfruit\b", "fruta"),
        (r"\bvegetable\b", "vegetal"),
        (r"\bvegetables\b", "vegetales"),
        (r"\bcleaned\b", "limpios"),
        (r"\bballs\b", "bolas"),
        (r"\bdispersed\b", "dispersados"),
        (r"\brapidly\b", "rápidamente"),
        (r"\bcherished\b", "preciado"),
        (r"\bdelicacy\b", "manjar"),
        (r"\btribe\b", "tribu"),
        (r"\bput into\b", "puestos en"),
        (r"\bbuckets\b", "recipientes"),
        (r"\blayers\b", "capas"),
        (r"\bleafy\b", "de hoja"),
        (r"\brape\b", "nabina"),
        (r"\bradish\b", "rábano"),
        (r"\bcauliflower\b", "coliflor"),
        (r"\blocated\b", "ubicado"),
        (r"\bNorth-East\b", "Noreste"),
        (r"\btoo\b", "demasiado"),
        (r"\bpungent\b", "picante"),
        (r"\bcobs\b", "mazorcas"),
        (r"\bMountain\b", "de montaña"),
    ]

    cleaned_count = 0

    for pid, name, desc, method, sub in products:
        new_name = name
        new_desc = desc or ""
        new_method = method or ""
        new_sub = sub or ""
        modified = False

        if new_desc:
            for pat, repl in word_map:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

        if new_name:
            for pat, repl in word_map:
                if re.search(pat, new_name, re.IGNORECASE):
                    new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE)
                    modified = True

        if new_method:
            for pat, repl in word_map:
                if re.search(pat, new_method, re.IGNORECASE):
                    new_method = re.sub(pat, repl, new_method, flags=re.IGNORECASE)
                    modified = True

        if new_sub:
            for pat, repl in word_map:
                if re.search(pat, new_sub, re.IGNORECASE):
                    new_sub = re.sub(pat, repl, new_sub, flags=re.IGNORECASE)
                    modified = True

        if modified:
            new_name = re.sub(r"\s+", " ", new_name).strip()
            new_desc = re.sub(r"\s+", " ", new_desc).strip()
            cursor.execute(
                "UPDATE products SET name = ?, description = ?, method = ?, substrate = ? WHERE id = ?",
                (new_name, new_desc if new_desc else None, new_method if new_method else None, new_sub if new_sub else None, pid)
            )
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
    print(f"\n🎉 Pulido cero tolerancia completado: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    zero_tolerance_cleaner()
