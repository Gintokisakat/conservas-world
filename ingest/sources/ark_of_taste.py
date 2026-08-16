"""
Fuente de ingesta para Alimentos Fermentados y Preservados Patrimoniales
del Arca del Gusto de Slow Food (Slow Food Ark of Taste).
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3

ARK_OF_TASTE_HERITAGE_PRODUCTS = [
    {
        "name": "Queso Cotija artesanal de montaña (DOP)",
        "description": "Queso mexicano ancestral de leche cruda de vaca producido exclusivamente durante la época de lluvias en la región montañosa entre Michoacán y Jalisco. Añejado en piezas gigantes con sal de mar marina.",
        "method": "Lacto-fermentación y Maduración",
        "substrate": "Leche Cruda de Vaca",
        "fermentation_time": "3-12 meses",
        "storage_life": "12-24 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Cotija_cheese.jpg/640px-Cotija_cheese.jpg"
    },
    {
        "name": "Aceto Balsamico Tradizionale di Modena DOP",
        "description": "Vinagre balsámico artesanal italiano envejecido durante un mínimo de 12 a 25 años en baterías de barricas de maderas nobles (roble, castaño, cerezo, fresno y enebro).",
        "method": "Fermentación Acética y Envejecimiento en Madera",
        "substrate": "Mosto de Uva Trebbiano / Lambrusco",
        "fermentation_time": "12-25 años",
        "storage_life": "Indefinido",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Traditional_balsamic_vinegar_bottles.jpg/640px-Traditional_balsamic_vinegar_bottles.jpg"
    },
    {
        "name": "Sardinas saladas en barril de madera (Sardinhas em lata/barril)",
        "description": "Conservación marina tradicional ibérica mediante salazón en húmedo y maduración en barriles de madera de pino. Patrimonio pesquero artesanal del Atlántico.",
        "method": "Salazón y Curado de Sal",
        "substrate": "Sardinas frescas",
        "fermentation_time": "2-6 meses",
        "storage_life": "12-24 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Salted_sardines.jpg/640px-Salted_sardines.jpg"
    },
    {
        "name": "Miso artesanal de soja negra de Tanba",
        "description": "Pasta de miso japonesa extremadamente rara producida con soja negra Kuromame cultivada en Tanba (Kyoto), fermentada pacientemente durante dos inviernos en tinos de cedro Kioke.",
        "method": "Fermentación Fúngica (Koji) y Enzimática",
        "substrate": "Soja Negra / Arroz Koji",
        "fermentation_time": "18-24 meses",
        "storage_life": "24-36 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Miso_paste.jpg/640px-Miso_paste.jpg"
    },
    {
        "name": "Chicha de Jora ancestral de maíz germinado",
        "description": "Bebida fermentada sagrada de los Andes elaborada a partir del malteado y cocción del maíz amarillo de Jora fermentado en vasijas de barro 'chombas' con levaduras autóctonas.",
        "method": "Fermentación Alcohólica / Silvestre",
        "substrate": "Maíz de Jora (Malteado)",
        "fermentation_time": "3-7 días",
        "storage_life": "1-2 semanas",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Chicha_de_jora_glass.jpg/640px-Chicha_de_jora_glass.jpg"
    },
    {
        "name": "Kimchi de rábano silvestre Mu-kkak-dugi",
        "description": "Kimchi artesanal coreano preparado con rábanos enteros de invierno curados en salmuera con hojas de mostaza, pasta de chiles secos Gochugaru y camarón fermentado Saeujeot.",
        "method": "Lacto-fermentación",
        "substrate": "Rábano coreano / Chile Gochugaru",
        "fermentation_time": "1-3 meses",
        "storage_life": "6-12 meses (refrigerado)",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Kkakdugi_1.jpg/640px-Kkakdugi_1.jpg"
    },
    {
        "name": "Queso Salers de leche cruda de vaca Salers (DOP)",
        "description": "Queso de pasta dura francés elaborado exclusivamente durante el periodo de pastoreo de verano en tina de madera 'gertout' con leche cruda e tibia recién ordeñada de vacas de raza Salers.",
        "method": "Lacto-fermentación y Maduración",
        "substrate": "Leche Cruda de Vaca Salers",
        "fermentation_time": "6-18 meses",
        "storage_life": "12 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Salers_cheese.jpg/640px-Salers_cheese.jpg"
    }
]


def ingest_ark_of_taste():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    print(f"🏛️ Ingestando {len(ARK_OF_TASTE_HERITAGE_PRODUCTS)} productos del Arca del Gusto de Slow Food...")
    added_count = 0

    for item in ARK_OF_TASTE_HERITAGE_PRODUCTS:
        cursor.execute("SELECT id FROM products WHERE name = ?", (item["name"],))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE products SET
                    description = ?, method = ?, substrate = ?,
                    fermentation_time = ?, storage_life = ?, image_url = ?, source_tag = 'ark_of_taste'
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ark_of_taste', 'active')
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
    print(f"\n🎉 Ingesta de Alimentos Patrimoniales del Arca del Gusto completada: {added_count} productos agregados.")

if __name__ == "__main__":
    ingest_ark_of_taste()
