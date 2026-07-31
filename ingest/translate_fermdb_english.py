"""
Script de traducción exhaustiva de oraciones y descripciones en inglés de FermDB y Wikipedia.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def translate_fermdb_english():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method FROM products")
    products = cursor.fetchall()

    print(f"📦 Traduciendo descripciones de FermDB/Wikipedia en {len(products)} productos...")
    updated_count = 0

    sentence_dict = [
        # Oraciones completas y sintagmas
        (r"\bis otherwise known as\b", "también es conocido como"),
        (r"\balso known as\b", "también conocido como"),
        (r"\bis a well known\b", "es un famoso"),
        (r"\bis a well-liked\b", "es un muy apreciado"),
        (r"\bis a popular\b", "es una popular"),
        (r"\bis a traditional\b", "es un tradicional"),
        (r"\bis a type of pickle\b", "es un tipo de encurtido"),
        (r"\bis a type of\b", "es un tipo de"),
        (r"\bis a\b", "es un"),
        (r"\bis an\b", "es un"),
        (r"\bis the historic name of\b", "es el nombre histórico de"),
        (r"\bproduced by\b", "producido por"),
        (r"\bproduced from\b", "producido a partir de"),
        (r"\bmade from\b", "elaborado a partir de"),
        (r"\bmade by\b", "elaborado mediante"),
        (r"\bmade with\b", "elaborado con"),
        (r"\bobtained from\b", "obtenido a partir de"),
        (r"\bprepared by steeping\b", "preparado mediante remojo de"),
        (r"\bprepared by\b", "preparado mediante"),
        (r"\bprepared from\b", "preparado a partir de"),
        (r"\bconsists in\b", "consiste en"),
        (r"\bcomposed of\b", "compuesto por"),
        (r"\bcoming in between\b", "con un contenido de entre"),
        (r"\boriginated in\b", "originario de"),
        (r"\bconsumed across\b", "consumido a lo largo de"),
        (r"\bconsumed in\b", "consumido en"),
        (r"\bused in\b", "utilizado en"),
        (r"\bused for\b", "utilizado para"),
        (r"\bused as\b", "utilizado como"),
        (r"\bas a flavoring agent for\b", "como agente aromatizante para"),
        (r"\bflavoring agent\b", "agente aromatizante"),
        (r"\bcereal grains in hot water\b", "granos de cereales en agua caliente"),
        (r"\bwet milling\b", "molienda en húmedo"),
        (r"\bsieving and fermenting for\b", "tamizado y fermentación durante"),
        (r"\bleft to ferment\b", "dejado a fermentar"),
        (r"\bfermenting for\b", "fermentando durante"),
        (r"\bsoaking in water for\b", "remojando en agua durante"),
        (r"\bcoarsely ground\b", "molienda gruesa"),
        (r"\bpeeled,washed and shredded\b", "pelado, lavado y rallado"),
        (r"\bpeeled\b", "pelado"),
        (r"\bwashed\b", "lavado"),
        (r"\bshredded\b", "rallado"),
        (r"\bchopped\b", "picado"),
        (r"\bsliced\b", "rebanado"),
        (r"\bdried\b", "deshidratado / seco"),
        (r"\bcooked\b", "cocinado"),
        (r"\bboiled\b", "hervido"),
        (r"\bsteamed\b", "al vapor"),
        (r"\broasted\b", "tostado"),
        (r"\bsmoked\b", "ahumado"),
        (r"\bfermented milk product\b", "producto lácteo fermentado"),
        (r"\bfermented milk drink\b", "bebida de leche fermentada"),
        (r"\bfermented milk\b", "leche fermentada"),
        (r"\bfermented rice\b", "arroz fermentado"),
        (r"\bfermented meat product\b", "producto cárnico fermentado"),
        (r"\bfermented meat\b", "carne fermentada"),
        (r"\bfermented fish\b", "pescado fermentado"),
        (r"\bfermented soybean\b", "soja fermentada"),
        (r"\bfermented soya\b", "soja fermentada"),
        (r"\bfermented cereal beverage\b", "bebida de cereal fermentado"),
        (r"\bfermented beverage\b", "bebida fermentada"),
        (r"\bfermented\b", "fermentado"),
        (r"\bdairy product\b", "producto lácteo"),
        (r"\bhousehold level\b", "nivel doméstico / artesanal"),
        (r"\bunpasteurised milk\b", "leche sin pasteurizar"),
        (r"\bunpasteurized milk\b", "leche sin pasteurizar"),
        (r"\bpasteurised milk\b", "leche pasteurizada"),
        (r"\braw cow's milk\b", "leche cruda de vaca"),
        (r"\braw milk\b", "leche cruda"),
        (r"\bcow milk\b", "leche de vaca"),
        (r"\bgoat milk\b", "leche de cabra"),
        (r"\bsheep milk\b", "leche de oveja"),
        (r"\bsheep’s milk\b", "leche de oveja"),
        (r"\bwhole or skimmed milk\b", "leche entera o desnatada"),
        (r"\bwhole milk\b", "leche entera"),
        (r"\bskimmed milk\b", "leche desnatada"),
        (r"\bsour milk\b", "leche agria / aceda"),
        (r"\bwhey queso\b", "requesón / queso de suero"),
        (r"\bwhey\b", "suero de leche"),
        (r"\bcottage queso\b", "queso fresco artesanal"),
        (r"\bhard queso\b", "queso de pasta dura"),
        (r"\bsoft queso\b", "queso de pasta blanda"),
        (r"\bgranular queso\b", "queso de textura granulada"),
        (r"\balpine queso\b", "queso alpino artesanal"),
        (r"\bacross South India and Sri Lanka\b", "en el sur de India y Sri Lanka"),
        (r"\bacross\b", "a lo largo de"),
        (r"\bduring the 13th century\b", "durante el siglo XIII"),
        (r"\bduring summer and overnight in winter\b", "en verano y durante la noche en invierno"),
        (r"\bhours\b", "horas"),
        (r"\bdays\b", "días"),
        (r"\bmonths\b", "meses"),
        (r"\byears\b", "años"),
        (r"\bthree months\b", "tres meses"),
        (r"\baged for at least\b", "madurado durante al menos"),
        (r"\baged for\b", "madurado durante"),
        (r"\baged\b", "madurado"),
        (r"\bby volume\b", "por volumen"),
        (r"\balcohol by volume\b", "alcohol por volumen"),
        (r"\balcohol content\b", "contenido alcohólico"),
        (r"\bcolorless liquor\b", "licor destilado incoloro"),
        (r"\bAfrican salad\b", "ensalada africana tradicional"),
        (r"\bdried meat product\b", "producto cárnico secado"),
        (r"\bsimilar to jerky\b", "similar a la cecina o tasajo"),
        (r"\bafrican locust bean\b", "algarrobo africano (Parkia biglobosa)"),
        (r"\bsweet-sour taste\b", "sabor agridulce"),
        (r"\beffervescent\b", "efervescente"),
        (r"\bcloudy\b", "turbio"),
        (r"\bbreakfast dish\b", "plato tradicional de desayuno"),
        (r"\bbreakfast\b", "desayuno"),
        (r"\bside product\b", "subproducto de elaboración"),
        (r"\bby-product\b", "subproducto"),
        (r"\bglutinous rice\b", "arroz glutinoso"),
        (r"\bsoybean dish\b", "plato a base de habas de soja"),
        (r"\bsoybean\b", "haba de soja"),
        (r"\bsoybeans\b", "habas de soja"),
        (r"\bsoya beans\b", "habas de soja"),
        (r"\blactic acid bacteria\b", "bacterias ácido-lácticas"),
        (r"\blactic acid\b", "ácido láctico"),
        (r"\bstarter culture\b", "cultivo iniciador"),
        (r"\bstarter\b", "iniciador"),
        (r"\b rice\b", " arroz"),
        (r"\b milk\b", " leche"),
        (r"\b meat\b", " carne"),
        (r"\b pork\b", " carne de cerdo"),
        (r"\b goat\b", " cabra"),
        (r"\b fish\b", " pescado"),
        (r"\b water\b", " agua"),
        (r"\b sugar\b", " azúcar"),
        (r"\b salt\b", " sal"),
        (r"\b garlic\b", " ajo"),
        (r"\b onion\b", " cebolla"),
        (r"\b onions\b", " cebollas"),
        (r"\b sweet\b", " dulce"),
        (r"\b fresh\b", " fresco"),
        (r"\b raw\b", " crudo"),
        (r"\b red\b", " rojo"),
        (r"\b green\b", " verde"),
        (r"\b black\b", " negro"),
        (r"\b white\b", " blanco"),
    ]

    for pid, name, desc, method in products:
        new_desc = desc if desc else ""
        new_method = method if method else ""
        modified = False

        if new_desc:
            for pat, repl in sentence_dict:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

        if new_method:
            for pat, repl in sentence_dict:
                if re.search(pat, new_method, re.IGNORECASE):
                    new_method = re.sub(pat, repl, new_method, flags=re.IGNORECASE)
                    modified = True

        if modified:
            cursor.execute("UPDATE products SET description = ?, method = ? WHERE id = ?", (new_desc if new_desc else None, new_method if new_method else None, pid))
            updated_count += 1

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
    print(f"\n🎉 Traducción de FermDB/Wikipedia completada: {updated_count} productos actualizados.")

if __name__ == "__main__":
    translate_fermdb_english()
