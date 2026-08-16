"""
Fuente de ingesta para Vinagres Caseros, Bebidas Vivas Ancestrales y Fermentos Koji.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3

CURATED_VINEGARS_AND_DRINKS = [
    {
        "name": "Vinagre de manzana casero con madre",
        "description": "Vinagre artesanal sin filtrar ni pasteurizar, obtenido mediante la fermentación acética de zumo o sidra de manzana por la bacteria Acetobacter aceti. Conserva la 'madre' de vinagre rica en enzimas y probióticos.",
        "method": "Fermentación Acética",
        "substrate": "Manzana / Sidra",
        "fermentation_time": "3-6 semanas",
        "storage_life": "12-24 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Apple_cider_vinegar_with_mother.jpg/640px-Apple_cider_vinegar_with_mother.jpg"
    },
    {
        "name": "Vinagre de piña artesanal (Vinagre de cáscara)",
        "description": "Vinagre tradicional latinoamericano preparado aprovechando las cáscaras y corazones de la piña madura fermentados con piloncillo o panela. Posee un aroma afrutado y acidez dulce característica.",
        "method": "Fermentación Acética",
        "substrate": "Piña / Piloncillo",
        "fermentation_time": "3-4 semanas",
        "storage_life": "12 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Pineapple_vinegar.jpg/640px-Pineapple_vinegar.jpg"
    },
    {
        "name": "Vinagre de vino tinto artesanal",
        "description": "Vinagre noble obtenido a partir del añejamiento de vino tinto artesanal en contacto con oxígeno y madre de vinagre. Excelente para marinados, escabeches y vinagretas culinarias.",
        "method": "Fermentación Acética",
        "substrate": "Uva / Vino Tinto",
        "fermentation_time": "1-3 meses",
        "storage_life": "Indefinido",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Red_Wine_Vinegar.jpg/640px-Red_Wine_Vinegar.jpg"
    },
    {
        "name": "Vinagre de arroz artesanal (Komezu)",
        "description": "Vinagre suave y ligeramente dulce tradicional de la gastronomía japonesa, fermentado a partir de sake o arroz cocido inoculado. Es suave para el paladar y esencial para el arroz de sushi.",
        "method": "Fermentación Acética",
        "substrate": "Arroz / Sake / Koji",
        "fermentation_time": "1-2 meses",
        "storage_life": "12-24 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Rice_vinegar.jpg/640px-Rice_vinegar.jpg"
    },
    {
        "name": "Vinagre de miel artesanal (Hydromel vinagre)",
        "description": "Vinagre milenario elaborado a partir del acificado de la hidromiel (miel de abejas diluida y fermentada). Cuenta con una acidez suave y profundas notas florales.",
        "method": "Fermentación Acética",
        "substrate": "Miel de Abejas",
        "fermentation_time": "2-3 meses",
        "storage_life": "24 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Honey_vinegar.jpg/640px-Honey_vinegar.jpg"
    },
    {
        "name": "Vinagre de Kombucha (Kombucha acificada)",
        "description": "Kombucha que ha extendido su fermentación por más de 30-60 días hasta convertirse en un vinagre vivo ultrapotente, repleto de ácido acético, ácido glucónico y enzimas digestivas.",
        "method": "Fermentación Acética",
        "substrate": "Té Verde / Té Negro / SCOBY",
        "fermentation_time": "1-2 meses",
        "storage_life": "12 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Kombucha_Jar.jpg/640px-Kombucha_Jar.jpg"
    },
    {
        "name": "Tepache de piña tradicional",
        "description": "Bebida viva efervescente y refrescante de baja graduación alcohólica (<1%), preparada fermentando las cáscaras de piña con piloncillo o panela y especias como canela y clavo de olor.",
        "method": "Fermentación Alcohólica / Acética",
        "substrate": "Piña / Canela / Piloncillo",
        "fermentation_time": "2-4 días",
        "storage_life": "5-7 días (refrigerado)",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tepache_mexicano.jpg/640px-Tepache_mexicano.jpg"
    },
    {
        "name": "Ginger Bug (Cultivo silvestre de jengibre)",
        "description": "Fermento madre silvestre efervescente elaborado a base de jengibre fresco, azúcar y agua. Se utiliza como cultivo iniciador para gasificar sodas artesanales de frutas y cerveza de jengibre.",
        "method": "Fermentación Alcohólica / Silvestre",
        "substrate": "Jengibre fresco",
        "fermentation_time": "5-7 días",
        "storage_life": "2-4 semanas (refrigerado)",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Ginger_bug.jpg/640px-Ginger_bug.jpg"
    },
    {
        "name": "Kvass de pan negro y remolacha",
        "description": "Bebida tónica fermentada ancestral de Europa del Este. El kvass tradicional de centeno y remolacha es efervescente, terroso, rico en lactobacilos y minerales.",
        "method": "Lacto-fermentación",
        "substrate": "Centeno / Remolacha",
        "fermentation_time": "3-7 días",
        "storage_life": "2 semanas (refrigerado)",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Kvass_in_glass.jpg/640px-Kvass_in_glass.jpg"
    },
    {
        "name": "Hidromiel artesanal (Mead)",
        "description": "La bebida alcohólica fermentada más antigua de la humanidad, producida mediante la fermentación de miel de abejas diluida en agua por levaduras silvestres o seleccionadas.",
        "method": "Fermentación Alcohólica",
        "substrate": "Miel de Abejas",
        "fermentation_time": "1-6 meses",
        "storage_life": "Variosaños",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Glass_of_mead.jpg/640px-Glass_of_mead.jpg"
    },
    {
        "name": "Kéfir de agua (Tibicos)",
        "description": "Bebida probiótica dulce y efervescente preparada fermentando agua azucarada con nódulos o gránulos de Tibicos (cultivo simbiótico de bacterias y levaduras).",
        "method": "Fermentación Alcohólica / Acética",
        "substrate": "Nódulos de Tibicos / Higo seco",
        "fermentation_time": "24-48 horas",
        "storage_life": "1-2 semanas (refrigerado)",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Water_kefir_grains.jpg/640px-Water_kefir_grains.jpg"
    },
    {
        "name": "Shio Koji (Adobo umami líquido)",
        "description": "Condimento tradicional japonés sazonador fermentado mezclando arroz koji (arroz inoculado con el hongo Aspergillus oryzae), sal y agua. Descompone las proteínas y resalta el sabor umami.",
        "method": "Koji / Umami",
        "substrate": "Arroz Koji / Sal marina",
        "fermentation_time": "7-10 días",
        "storage_life": "6 meses (refrigerado)",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Shio_koji.jpg/640px-Shio_koji.jpg"
    },
    {
        "name": "Miso de garbanzo artesanal",
        "description": "Variación moderna y cremosa del miso tradicional, elaborada sustituyendo la soja por garbanzos cocidos fermentados con arroz koji y sal. Aporta un profundo sabor umami salado y mantecoso.",
        "method": "Koji / Umami",
        "substrate": "Garbanzo / Arroz Koji",
        "fermentation_time": "3-12 meses",
        "storage_life": "12-24 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Miso_paste.jpg/640px-Miso_paste.jpg"
    }
]


def ingest_vinegars_and_drinks():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    print(f"📦 Ingestando {len(CURATED_VINEGARS_AND_DRINKS)} vinagres, bebidas vivas y fermentos koji...")
    added_count = 0

    for item in CURATED_VINEGARS_AND_DRINKS:
        cursor.execute("SELECT id FROM products WHERE name = ?", (item["name"],))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE products SET
                    description = ?, method = ?, substrate = ?,
                    fermentation_time = ?, storage_life = ?, image_url = ?, source_tag = 'vinegar_curated'
                WHERE id = ?
            """, (
                item["description"], item["method"], item["substrate"],
                item["fermentation_time"], item["storage_life"], item["image_url"],
                row[0]
            ))
        else:
            cursor.execute("""
                INSERT INTO products (
                    name, description, method, substrate, fermentation_time,
                    storage_life, image_url, source_tag, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'vinegar_curated', 'active')
            """, (
                item["name"], item["description"], item["method"], item["substrate"],
                item["fermentation_time"], item["storage_life"], item["image_url"]
            ))
            added_count += 1

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
    print(f"\n🎉 Ingesta de Vinagres y Bebidas Vivas completada: {added_count} productos nuevos agregados.")

if __name__ == "__main__":
    ingest_vinegars_and_drinks()
