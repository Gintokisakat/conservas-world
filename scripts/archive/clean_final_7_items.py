import sqlite3

conn = sqlite3.connect("data/build.db")
cursor = conn.cursor()

fixes = {
    2288: ("Esencia de vinagre (24.9% acidez)", "Agua, acidulante: ácido acético."),
    2311: ("Vinagre de manzana orgánico sin filtrar 5%", "Vinagre de manzana orgánico sin filtrar prensado en frío."),
    2793: ("Alcaparras en aceite", None),
    2802: ("Alcaparras sazonadas en aceite de oliva", "Alcaparras 55%, aceite de oliva 42%, vinagre de vino, sal, ajo, orégano, corrector de acidez: ácido cítrico."),
    2805: ("Alcaparras en aceite de girasol", "Alcaparras 61%, aceite de girasol, vinagre de vino, sal, corrector de acidez: ácido cítrico."),
    2898: ("Pasta de anchoas del Cantábrico", "Anchoas (87.5%), aceite de oliva, sal, clavos de olor."),
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

print("✅ Los últimos 7 elementos han sido completamente traducidos al español.")
