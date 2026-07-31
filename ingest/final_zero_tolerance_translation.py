"""
Script de traducción cero tolerancia absoluta para eliminar cualquier término o ruido extranjero restante.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def final_zero_tolerance():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method, substrate FROM products")
    products = cursor.fetchall()

    print(f"📦 Aplicando pase cero tolerancia absoluto en {len(products)} productos...")

    final_map = [
        # Títulos específicos
        (r"^Chucrut \(Chucrut \(Sauerkraut\)\)", "Chucrut tradicional"),
        (r"^Sour repollo\b", "Repollo agrio"),
        (r"^Queso Blue\b", "Queso azul"),
        (r"\bQueso Bregenzerwalder Mountain\b", "Queso de montaña Bregenzerwälder"),
        (r"\bOlives\b", "Aceitunas"),

        # Términos en descripciones
        (r"\bGouda-style\b", "estilo Gouda"),
        (r"\bIndonesian style\b", "estilo indonesio"),
        (r"\bstyle\b", "estilo"),
        (r"\bSauerkraut\b", "chucrut"),
        (r"\bsauerkraut\b", "chucrut"),
        (r"\bsauce\b", "salsa"),
        (r"\bcheese\b", "queso"),
        (r"\boil\b", "aceite"),
        (r"\bgarlic\b", "ajo"),
        (r"\byeast\b", "levadura"),
        (r"\bvin doux naturel\b", "vino dulce natural"),
        (r"\bfamous\b", "famoso"),
        (r"\bLean molido\b", "carne magra molida"),
        (r"\bpig skin\b", "piel de cerdo"),
        (r"\bolive tree\b", "olivo"),
        (r"\bcrudo form\b", "forma cruda"),
        (r"\bvery amargo\b", "muy amargo"),
        (r"\btherefore\b", "por lo tanto"),
        (r"\bcured\b", "curado"),
        (r"\bprominent\b", "destacado"),
        (r"\bmalolactic\b", "maloláctica"),
        (r"\bpreserve\b", "conserva"),
        (r"\bthrough\b", "a través de"),
        (r"\blacto-fermentation\b", "lactofermentación"),
        (r"\blate harvest\b", "cosecha tardía"),
        (r"\bpicked\b", "recolectadas"),
        (r"\bdate\b", "fecha"),
        (r"\bleading\b", "conduciendo a"),
        (r"\blit\.\b", "literalmente"),
        (r"\byellow-colored\b", "de color amarillo"),
        (r"\bsaline\b", "salina"),
        (r"\bprotein-rich\b", "rico en proteínas"),
        (r"\bfood\b", "alimento"),
        (r"\bsolid state\b", "estado sólido"),
    ]

    cleaned_count = 0

    for pid, name, desc, method, sub in products:
        new_name = name
        new_desc = desc or ""
        new_method = method or ""
        new_sub = sub or ""
        modified = False

        if new_desc:
            for pat, repl in final_map:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

        if new_name:
            for pat, repl in final_map:
                if re.search(pat, new_name, re.IGNORECASE):
                    new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE)
                    modified = True

        if new_method:
            for pat, repl in final_map:
                if re.search(pat, new_method, re.IGNORECASE):
                    new_method = re.sub(pat, repl, new_method, flags=re.IGNORECASE)
                    modified = True

        if new_sub:
            for pat, repl in final_map:
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
    print(f"\n🎉 Pase cero tolerancia absoluto completado: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    final_zero_tolerance()
