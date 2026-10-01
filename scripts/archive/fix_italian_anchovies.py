import sqlite3

conn = sqlite3.connect("data/build.db")
cursor = conn.cursor()

fixes = {
    2918: ("Filetes de anchoa del Cantábrico en aceite de oliva #2918", None),
    2923: ("Filetes de anchoas marinadas en aceite", None),
    2936: ("Filetes de anchoa marinados en aceite", None),
    2937: ("Filetes de anchoa en aceite #2937", None),
    2938: ("Filetes de anchoa en aceite de oliva #2938", None),
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

print("✅ Todos los registros de anchoas italianas traducidos al 100%.")
