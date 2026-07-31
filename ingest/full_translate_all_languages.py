"""
Script completo de traducción y limpieza multilingüe para Conservas del Mundo (`data/build.db`).
Traduce productos en francés, italiano, holandés, alemán, sueco e inglés al español,
limpia caracteres escapados (d\'orange -> d'orange) y signos de puntuación iniciales.
"""

import sqlite3
import re

def full_translate():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Procesando {len(products)} productos para traducción y limpieza multilingüe...")

    updated_count = 0

    vocab = [
        # Caracteres rotos / Escapes / Prefijos ruidosos
        (r"\\'", "'"),
        (r"^\.([A-ZáéíóúñÁÉÍÓÚÑ])", r"\1"),
        (r"^\s*[\.\,\-\_\:\;]+\s*", ""),
        (r"\bA Lightly Sopa\b", "Sopa"),
        (r"\bAH Terra Orgánico seitan wokreepjes teriyaki\b", "Tiras de seitán orgánico teriyaki para wok"),
        
        # Frutas & Vegetales (Francés / Holandés / Italiano)
        (r"\bFraises d'Aquitaine\b", "Fresas de Aquitania"),
        (r"\bFraises\b", "Fresas"),
        (r"\bFramboises\b", "Frambuesas"),
        (r"\bAbricots\b", "Albaricoques / Damascos"),
        (r"\bCerises\b", "Cerezas"),
        (r"\bPrunes\b", "Ciruelas"),
        (r"\bPêches\b", "Melocotones / Duraznos"),
        (r"\bAgrumes\b", "Cítricos"),
        (r"\bOeufs Marinés\b", "Huevos marinados / encurtidos"),
        (r"\bOeufs\b", "Huevos"),
        (r"\bAugurken zoetzuur\b", "Pepinillos agridulces"),
        (r"\bAugurken\b", "Pepinillos encurtidos"),
        (r"\bZoetzuur\b", "Agridulce"),
        
        # Pescados & Mariscos (Italiano / Francés / Inglés)
        (r"\bAlbacore Tuna \| In Brine\b", "Atún blanco en salmuera"),
        (r"\bAlici marinate\b", "Anchoas marinadas (Alici)"),
        (r"\bAlici salate\b", "Anchoas saladas"),
        (r"\bAlici\b", "Anchoas"),
        (r"\bSalmone islandese aff\.a freddo\b", "Salmón islandés ahumado en frío"),
        (r"\bSalmone\b", "Salmón"),
        (r"\bSmoked Haddock & Salmon Chowder\b", "Sopa cremosa de eglefino y salmón ahumado"),
        (r"\bAcciughe del mar cantabrico\b", "Anchoas del mar Cantábrico"),
        (r"\bAcciughe salate\b", "Anchoas saladas en salmuera"),
        (r"\bAcciughe\b", "Anchoas"),
        (r"\bsardines de l'Île de Ré\b", "Sardinas de la Isla de Ré"),
        (r"\bSardines\b", "Sardinas"),

        # Lácteos & Yogures (Francés / Inglés)
        (r"\bNatural Sans Sucre\b", "Natural Sin Azúcar"),
        (r"\bsans sucres ajoutes\b", "sin azúcares añadidos"),
        (r"\bgout fraise\b", "sabor fresa"),
        (r"\bgout multifruit\b", "sabor multifruta"),
        (r"\bAcidophilus Milk\b", "Leche acidófila fermentada"),
        (r"\bGerookte Tofu\b", "Tofu ahumado"),
        (r"\bAlspånsrökt Tempeh\b", "Tempeh ahumado con madera de aliso"),
        (r"\bAged Red Miso\b", "Miso rojo añejado"),
        (r"\bAigre-doux\b", "Preparado agridulce"),
        (r"\bBiologische\b", "Orgánico"),
        (r"\bBiologique\b", "Orgánico"),
        (r"\bGerookte\b", "Ahumado"),
        (r"\bGerookt\b", "Ahumado"),
        (r"\bVierge extra\b", "Virgen extra"),
        (r"\bNature\b", "Natural"),
        (r"\bAceton Balsamico di Modena I\.G\.P\.\b", "Vinagre balsámico de Módena IGP"),
        (r"\bAlus BREWDOG PUNK ipa\b", "Cerveza BrewDog Punk IPA"),
        (r"\bSpecialité d'orange\b", "Especialidad de naranja"),
    ]

    for pid, orig_name, desc, source in products:
        new_name = orig_name.strip()
        was_modified = False

        for pat, repl in vocab:
            if re.search(pat, new_name, re.IGNORECASE):
                new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                was_modified = True

        if new_name.startswith("(Mermelada)"):
            new_name = new_name.replace("(Mermelada)", "Mermelada de").strip()
            was_modified = True

        new_name = re.sub(r"\s+", " ", new_name).strip()

        if was_modified and new_name != orig_name and len(new_name) > 1:
            cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (new_name, pid))
            conflict = cursor.fetchone()
            if conflict:
                candidate_name = f"{new_name} #{pid}"
                cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (candidate_name, pid))
                if cursor.fetchone():
                    candidate_name = f"{new_name} ({source} #{pid})"
                new_name = candidate_name

            # Guardar alias original
            cursor.execute("SELECT id FROM product_aliases WHERE product_id = ? AND name = ?", (pid, orig_name))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO product_aliases (product_id, name, language) VALUES (?, ?, ?)", (pid, orig_name, "orig"))

            cursor.execute("UPDATE products SET name = ? WHERE id = ?", (new_name, pid))
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
    print(f"\n🎉 Traducción multilingüe completada: {updated_count} productos actualizados.")

if __name__ == "__main__":
    full_translate()
