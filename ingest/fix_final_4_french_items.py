import sqlite3

conn = sqlite3.connect("data/build.db")
cursor = conn.cursor()

fixes = {
    2469: ("Mermelada de fresa (430 g)", "Fresas (56%), azúcar, gelificante (E-440) y acidulante (E-330)."),
    2513: ("Gerblé - Mermelada de albaricoque sin azúcar añadido (320 g)", "Albaricoques 50%, agua, edulcorante (maltitoles), fibra vegetal (dextrina de trigo), gelificante (pectinas), acidulante (ácido cítrico), corrector de acidez (citratos de calcio), antioxidante (ácido ascórbico), edulcorante (sucralosa), conservante (sorbato de potasio)."),
    2732: ("Papayas y piñas deshidratadas y azucaradas", "Azúcar, piña, papaya, acidulante E330, conservantes: E220, E223 (sulfito)."),
    2762: ("Chocolate negro Nestlé L'Atelier con naranja confitada", "Pasta de cacao (África Occidental, Ecuador), azúcar, cortezas de naranja confitadas 10% [cortezas de naranja, jarabe de glucosa y fructosa, dextrosa, azúcar, aroma natural de naranja, acidulante (ácido cítrico)], materia grasa láctea anhidra, manteca de cacao, emulgente (lecitina de girasol), aroma natural de vainilla. Cacao: 54% mínimo en el chocolate negro. Puede contener: huevo, gluten, frutos de cáscara."),
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

print("✅ Todos los productos restantes 100% traducidos al español.")
