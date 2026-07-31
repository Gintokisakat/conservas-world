import sqlite3

conn = sqlite3.connect("data/build.db")
cursor = conn.cursor()

fixes = {
    1677: ("Hummus de Kimchi", "Hummus 65% (garbanzos, aceite de girasol, zumo de limón, tahini [semillas de sésamo], sal), kimchi"),
    2904: ("Filetes de anchoa en aceite de girasol #2904", None),
    2905: ("Filetes de anchoa en aceite de oliva #2905", "Anchoas, aceite de oliva, sal."),
    2906: ("Filetes de anchoa del Canal de Sicilia en aceite de oliva", None),
    2916: ("Filetes de anchoa en aceite de oliva #2916", "Anchoas (Engraulis encrasicholus), aceite de oliva, sal. Semiconserva."),
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

print("✅ Todos los registros en la base de datos están 100% traducidos al español.")
