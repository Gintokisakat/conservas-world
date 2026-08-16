"""
Fuente de ingesta expandida para Alimentos Fermentados y Preservados Patrimoniales
del Arca del Gusto de Slow Food (Slow Food Ark of Taste).
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3

ARK_OF_TASTE_HERITAGE_PRODUCTS = [
    {
        "name": "Queso Cotija artesanal de montaña (DOP)",
        "description": "Queso mexicano ancestral de leche cruda de vaca producido exclusivamente durante la época de lluvias en la región montañosa entre Michoacán y Jalisco. Añejado en piezas gigantes con sal marina.",
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
        "name": "Sardinas saladas en barril de madera",
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
    },
    {
        "name": "Asín Tibuok (Sal artesanal marina en coco)",
        "description": "Patrimonio artesanal filipino en peligro de extinción: sal marina ahumada y moldeada en cáscaras de coco curadas en salmuera durante meses. Posee un sabor dulce, ahumado y salino único.",
        "method": "Salazón y Ahumado Ancestral",
        "substrate": "Agua de Mar / Cáscara de Coco",
        "fermentation_time": "3-6 meses",
        "storage_life": "Indefinido",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Asin_tibuok.jpg/640px-Asin_tibuok.jpg"
    },
    {
        "name": "Queso Serra da Estrela (DOP)",
        "description": "Queso portugués cremoso y mantecoso de leche cruda de oveja de raza Serra da Estrela, cuajado artesanalmente utilizando la flor silvestre del cardo (Cynara cardunculus).",
        "method": "Lacto-fermentación y Coagulación por Cardo",
        "substrate": "Leche Cruda de Oveja / Flor de Cardo",
        "fermentation_time": "30-60 días",
        "storage_life": "3-6 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Queijo_Serra_da_Estrela.jpg/640px-Queijo_Serra_da_Estrela.jpg"
    },
    {
        "name": "Queijo de Cabra Transmontano (DOP)",
        "description": "Queso curado duro y picante producido en Trás-os-Montes (Portugal) con leche cruda de cabra de raza Serrana. Su corteza se unta con pimentón dulce y aceite de oliva.",
        "method": "Lacto-fermentación y Maduración",
        "substrate": "Leche Cruda de Cabra Serrana",
        "fermentation_time": "60-180 días",
        "storage_life": "12 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Queijo_de_Cabra_Transmontano.jpg/640px-Queijo_de_Cabra_Transmontano.jpg"
    },
    {
        "name": "Skyr artesanal de leche cruda de oveja",
        "description": "Producto lácteo espeso y probiótico icónico de Islandia elaborado artesanalmente desde la era vikinga mediante la fermentación de suero lácteo concentrado con cultivos nativos.",
        "method": "Lacto-fermentación Concentrada",
        "substrate": "Leche de Oveja / Suero de Skyr",
        "fermentation_time": "24-48 horas",
        "storage_life": "1-2 meses (refrigerado)",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Skyr.jpg/640px-Skyr.jpg"
    },
    {
        "name": "Queso de bola de Ocosingo artesanal",
        "description": "Queso artesanal chiapaneco único en su clase: una bola de queso fresco de vaca envuelta en una doble cubierta o cascarón duro y ceroso de queso ácido curado.",
        "method": "Lacto-fermentación Doble",
        "substrate": "Leche de Vaca de Chiapas",
        "fermentation_time": "1-3 meses",
        "storage_life": "6 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Queso_bola_Ocosingo.jpg/640px-Queso_bola_Ocosingo.jpg"
    },
    {
        "name": "Pecorino di Farindola",
        "description": "Queso italiano histórico elaborado exclusivamente en Abruzzo utilizando cuajo de estómago de cerdo, lo que le confiere un perfil aromático intenso y una textura mantecosa irrepetible.",
        "method": "Lacto-fermentación con Cuajo Porcino",
        "substrate": "Leche Cruda de Oveja",
        "fermentation_time": "3-12 meses",
        "storage_life": "12 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Pecorino_Farindola.jpg/640px-Pecorino_Farindola.jpg"
    },
    {
        "name": "Garum artesanal marino de caballa",
        "description": "Recreación histórica del célebre condimento umami líquido de la antigua Roma y Grecia, elaborado mediante la autólisis enzimática y fermentación de pescado en salmuera al sol.",
        "method": "Autólisis Enzimática en Salmuera",
        "substrate": "Caballa / Sal Marina",
        "fermentation_time": "3-6 meses",
        "storage_life": "24 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Garum_sauce.jpg/640px-Garum_sauce.jpg"
    },
    {
        "name": "Attiéké de yuca fermentada",
        "description": "Patrimonio gastronómico de Costa de Marfil (reconocido por UNESCO): couscous granulado elaborado a base de pulpa de yuca agria fermentada al aire y al vapor.",
        "method": "Lacto-fermentación de Tubérculo",
        "substrate": "Yuca / Casava",
        "fermentation_time": "3-5 días",
        "storage_life": "1-2 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Attieke_bowl.jpg/640px-Attieke_bowl.jpg"
    },
    {
        "name": "Kishk de trigo burgol y leche fermentada",
        "description": "Conservado ancestral de Medio Oriente (Líbano/Siria/Jordania): mezcla secada al sol de trigo burgol cocido y yogurt agrio o laban, molida en un fino polvo salado y acentuado.",
        "method": "Lacto-fermentación y Deshidratado al Sol",
        "substrate": "Trigo Burgol / Yogurt Agrio (Laban)",
        "fermentation_time": "1-2 semanas",
        "storage_life": "12-24 meses",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Kishk_powder.jpg/640px-Kishk_powder.jpg"
    },
    {
        "name": "Ogi / Pap de maíz fermentado",
        "description": "Pudín/crema de fermentación láctica tradicional de Nigeria y África Occidental, preparado mediante el remojo e inóculo de granos de maíz, mijo o sorgo.",
        "method": "Lacto-fermentación de Cereal",
        "substrate": "Maíz / Mijo / Sorgo",
        "fermentation_time": "2-4 días",
        "storage_life": "1-2 semanas",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Ogi_pap_bowl.jpg/640px-Ogi_pap_bowl.jpg"
    }
]

HERITAGE_SEARCH_KEYWORDS = [
    "parmigiano", "roquefort", "gorgonzola", "stilton", "manchego", "pecorino",
    "balsamico", "garum", "kimchi", "sauerkraut", "chicha", "miso", "sardina",
    "kombucha", "cotija", "salers", "skyr", "attiéké", "kishk", "ogi", "kvass", "tepache"
]


def ingest_ark_of_taste():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    print(f"🏛️ Ingestando {len(ARK_OF_TASTE_HERITAGE_PRODUCTS)} productos nuevos del Arca del Gusto de Slow Food...")
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

    # Etiquetar productos preexistentes que corresponden al patrimonio Arca del Gusto
    tagged_count = 0
    for kw in HERITAGE_SEARCH_KEYWORDS:
        cursor.execute("""
            UPDATE products
            SET source_tag = 'ark_of_taste'
            WHERE (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)
              AND (source_tag IS NULL OR source_tag IN ('regional', 'fdfdb', 'wikipedia', 'fermdb'))
        """, (f"%{kw}%", f"%{kw}%"))
        tagged_count += cursor.rowcount

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

    cursor.execute("SELECT COUNT(*) FROM products WHERE source_tag = 'ark_of_taste'")
    total_ark_count = cursor.fetchone()[0]

    conn.close()
    print(f"\n🎉 Ingesta y etiquetado del Arca del Gusto completado:")
    print(f"   • Productos específicos agregados: {added_count}")
    print(f"   • Total de conservas patrimoniales etiquetadas como Arca del Gusto: {total_ark_count}")

if __name__ == "__main__":
    ingest_ark_of_taste()
