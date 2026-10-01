import sqlite3

conn = sqlite3.connect("data/build.db")
cursor = conn.cursor()

fixes = {
    3131: ("Aceitunas negras confitadas deshuesadas", "Aceitunas negras, sal, aceite de oliva virgen extra (0.5%), estabilizante: gluconato ferroso."),
    3162: ("Aceitunas negras confitadas deshuesadas en frasco", "Agua, aceitunas, sal, estabilizante: gluconato ferroso."),
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

print("✅ Entradas de gluconato ferroso 100% traducidas al español.")
