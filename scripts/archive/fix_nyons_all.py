import sqlite3

conn = sqlite3.connect("data/build.db")
cursor = conn.cursor()

fixes = {
    3185: ("Aceitunas negras de Nyons (Variedad 3185)", "Aceitunas negras, sal"),
    3202: ("Aceitunas negras AOP Nyons", "Aceitunas negras AOP Nyons, agua, sal"),
    3205: ("Aceitunas negras de Nyons AOP", "Aceitunas negras al natural, sal marina."),
    3212: ("Aceitunas negras de Nyons (Variedad 3212)", "Aceitunas negras al natural (Origen Francia), sal marina"),
    3219: ("Aceitunas negras de Nyons AOP pasteurizadas", "Aceitunas negras de Nyons, sal."),
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

print("✅ Entradas de Nyons AOP 100% traducidas al español.")
