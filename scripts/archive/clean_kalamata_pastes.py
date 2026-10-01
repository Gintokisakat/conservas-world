import sqlite3

conn = sqlite3.connect("data/build.db")
cursor = conn.cursor()

fixes = {
    3178: ("Pasta de aceitunas Kalamata", "96% aceitunas Kalamata (aceitunas, agua, sal), aceite de oliva, pimiento rojo, vinagre de vino, orégano, corrector de acidez: ácido láctico."),
    3200: ("Aceitunas Kalamata grandes deshuesadas", "Aceitunas Kalamata, agua, sal marina, vinagre de vino tinto, aceite de oliva virgen extra (2%), corrector de acidez (ácido láctico)."),
    3210: ("Aceitunas Kalamata deshuesadas orgánicas", "Aceitunas negras*, agua, sal marina, vinagre de vino tinto* * agricultura ecológica."),
}

for pid, (name, desc) in fixes.items():
    cursor.execute("UPDATE products SET name = ?, description = ? WHERE id = ?", (name, desc, pid))

conn.commit()

# Reconstruir FTS5
cursor.execute("DROP TABLE IF EXISTS products_fts;")
cursor.execute("CREATE VIRTUAL TABLE products_fts USING fts5(name, description, content=products, content_rowid=id);")
cursor.execute('INSERT INTO products_fts(products_fts) VALUES("rebuild");')
conn.commit()
conn.close()

print("✅ Entradas de Kalamata 100% traducidas al español.")
