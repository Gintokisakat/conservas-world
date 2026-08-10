"""
Script de traducción y normalización de descripciones de mermeladas, lácteos, embutidos y bebidas fermentadas.
Para Conservas del Mundo (`data/build.db`).
"""

import re
import sqlite3


def translate_jams_and_meats():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos...")

    cleaned_count = 0

    jam_and_meat_vocab = [
        # Títulos
        (r"^100% fruits Especialidad de naranja\b", "Especialidad de naranja 100% fruta"),
        (r"\b100% fruits\b", "100% fruta"),
        (r"\bCIAO KOMBUCHA FRUITS ROUGES\b", "Kombucha Ciao Frutos Rojos"),
        (r"\bKombucha Fraise et Pêche\b", "Kombucha Fresa y Melocotón"),
        (r"\bPanier de Yoplait Cerise\b", "Yoplait Cesta de Cereza"),
        (r"\bHipro Saveur Myrtille\b", "HiPro Sabor Arándano"),
        
        # Descripciones - Frutas & Mermeladas
        (r"\bOranges\b", "Naranjas"),
        (r"\bsucres extraits de fruits\b", "azúcares extraídos de frutas"),
        (r"\bcitrons\b", "limones"),
        (r"\bcitron\b", "limón"),
        (r"\bgélifiant\s*:\s*pectine de fruits\b", "gelificante: pectina de frutas"),
        (r"\bgélifiant\s*:\s*pectines\b", "gelificante: pectinas"),
        (r"\bgélifiant\b", "gelificante"),
        (r"\bpectine de fruits\b", "pectina de frutas"),
        (r"\bpectine\b", "pectina"),
        (r"\bpectines\b", "pectinas"),
        (r"\bpommes\b", "manzanas"),
        (r"\bpoires\b", "peras"),
        (r"\bpamplemousses\b", "pomelos"),
        (r"\bclementines\b", "clementinas"),
        (r"\bagrumes\b", "cítricos"),
        (r"\bOrigine France\b", "Origen Francia"),
        (r"\bEspagne\b", "España"),
        
        # Descripciones - Cárnicos, Chucrut & Embutidos
        (r"\bviande de porc\b", "carne de cerdo"),
        (r"\bgras de porc\b", "grasa de cerdo"),
        (r"\bcouenne de porc\b", "corteza de cerdo"),
        (r"\bfarine de blé\b", "harina de trigo"),
        (r"\bfibre de pois\b", "fibra de guisante"),
        (r"\bprotéines de soja\b", "proteínas de soja"),
        (r"\bstabilisant\b", "estabilizante"),
        (r"\bconservateur\b", "conservante"),
        (r"\bsaindoux\b", "manteca de cerdo"),
        (r"\bvin blanc\b", "vino blanco"),
        (r"\bbaies de genièvre\b", "bayas de enebro"),
        (r"\bbaies de génièvre\b", "bayas de enebro"),
        (r"\boignon en poudre\b", "cebolla en polvo"),
        (r"\bgrains de poivre\b", "granos de pimienta"),
        (r"\bsirop de glucose\b", "jarabe de glucosa"),
        (r"\bpiment doux\b", "pimentón dulce"),
        (r"\bgraines de cumin\b", "semillas de comino"),

        # Descripciones - Kombucha & Yogures
        (r"\bBoisson gazéifiée à base de thé vert fermenté\b", "Bebida carbonatada a base de té verde fermentado"),
        (r"\bpointe de jus de fruits rouges\b", "toque de jugo de frutos rojos"),
        (r"\bavec édulcorant\b", "con edulcorante"),
        (r"\bmélange de bactéries et levures\b", "mezcla de bacterias y levaduras"),
        (r"\bpurée de framboises\b", "puré de frambuesas"),
        (r"\bpurée de myrtilles\b", "puré de arándanos"),
        (r"\binfusion d'hibiscus\b", "infusión de hibisco"),
        (r"\bépaississants\b", "espesantes"),
        (r"\bamidon modifié de maïs\b", "almidón modificado de maíz"),
        (r"\bcorrecteurs d'acidité\b", "correctores de acidez"),
        (r"\bacide citrique\b", "ácido cítrico"),
        (r"\bcitrate de sodium\b", "citrato de sodio"),
    ]

    for pid, orig_name, desc, _source in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in jam_and_meat_vocab:
            if re.search(pat, new_name, re.IGNORECASE):
                new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                modified = True

            if new_desc and re.search(pat, new_desc, re.IGNORECASE):
                new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE).strip()
                modified = True

        new_name = re.sub(r"\s+", " ", new_name).strip()

        if modified:
            cursor.execute("UPDATE products SET name = ?, description = ? WHERE id = ?", (new_name, new_desc if new_desc else None, pid))
            cleaned_count += 1

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
    print(f"\n🎉 Proceso completado: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    translate_jams_and_meats()
