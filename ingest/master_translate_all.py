"""
Script de traducción universal masiva para Conservas del Mundo (`data/build.db`).
Traduce exhaustivamente todos los títulos y descripciones en alemán, italiano, polaco, francés e inglés al español,
y reindexa FTS5.
"""

import sqlite3
import re

def master_translate():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Iniciando traducción universal masiva sobre {len(products)} productos...")

    cleaned_count = 0

    translations = [
        # --- 🇩🇪 Vocabulario Alemán ---
        (r"\bSojabohnen\b", "habas de soja"),
        (r"\bWachtelbohnen\b", "alubias / frijoles"),
        (r"\bRohrzucker\b", "azúcar de caña"),
        (r"\bMaisstärke\b", "almidón de maíz"),
        (r"\bKartoffelstärke\b", "almidón de patata"),
        (r"\bBranntweinessig\b", "vinagre de alcohol"),
        (r"\bCitronensäure\b", "ácido cítrico"),
        (r"\bZitronensäure\b", "ácido cítrico"),
        (r"\bSäuerungsmittel\b", "acidulante"),
        (r"\bAntioxidationsmittel\b", "antioxidante"),
        (r"\bSpeisesalz\b", "sal común"),
        (r"\bMeersalz\b", "sal marina"),
        (r"\bSenfsaat\b", "semillas de mostaza"),
        (r"\bSenfkörner\b", "semillas de mostaza"),
        (r"\bZwiebeln\b", "cebollas"),
        (r"\bKnoblauch\b", "ajo"),
        (r"\bGurken\b", "pepinillos"),
        (r"\bWasser\b", "agua"),
        (r"\bTrinkwasser\b", "agua potable"),
        (r"\bZucker\b", "azúcar"),
        (r"\bEssig\b", "vinagre"),
        (r"\bGewürze\b", "especias"),
        (r"\bMilchsäure\b", "ácido láctico"),
        (r"\bHefe\b", "levadura"),
        (r"\bBohnen\b", "alubias"),
        (r"\baus kontrolliert biologischem Anbau\b", "(de cultivo ecológico controlado)"),
        (r"\baus biologischem Anbau\b", "(de cultivo ecológico)"),
        (r"\baus biologischer Landwirtschaft\b", "(de agricultura ecológica)"),

        # --- 🇮🇹 Vocabulario Italiano ---
        (r"\bAceto di mele\b", "vinagre de manzana"),
        (r"\bAceto balsamico\b", "vinagre balsámico"),
        (r"\bAceto\b", "vinagre"),
        (r"\bAcqua\b", "agua"),
        (r"\bZucchero\b", "azúcar"),
        (r"\bSale\b", "sal"),
        (r"\bAglio\b", "ajo"),
        (r"\bCipolla\b", "cebolla"),
        (r"\bCipolle\b", "cebollas"),
        (r"\bPomodoro\b", "tomate"),
        (r"\bFormaggio\b", "queso"),
        (r"\bOlio d'oliva\b", "aceite de oliva"),
        (r"\bLatte\b", "leche"),
        (r"\bLievito\b", "levadura"),
        (r"\bBiologico\b", "orgánico"),

        # --- 🇵🇱 Vocabulario Polaco ---
        (r"\bczosnek marynowany\b", "ajo marinado"),
        (r"\bczosnek\b", "ajo"),
        (r"\bocet winny\b", "vinagre de vino"),
        (r"\bOcet\b", "vinagre"),
        (r"\bOgórki\b", "pepinillos"),
        (r"\bKapusta\b", "repollo"),
        (r"\bWoda\b", "agua"),
        (r"\bCukier\b", "azúcar"),
        (r"\bSól\b", "sal"),
        (r"\bChleb\b", "pan"),

        # --- 🇫🇷 Vocabulario Francés ---
        (r"\bEau\b", "agua"),
        (r"\bSucre\b", "azúcar"),
        (r"\bSel\b", "sal"),
        (r"\bVinaigre\b", "vinagre"),
        (r"\bOignon\b", "cebolla"),
        (r"\bOignons\b", "cebollas"),
        (r"\bAil\b", "ajo"),
        (r"\bHuile\b", "aceite"),
        (r"\bMoutarde\b", "mostaza"),
        (r"\bLait\b", "leche"),
        (r"\bLevure\b", "levadura"),
        (r"\bPoivre\b", "pimienta"),
        (r"\bPiment\b", "chile"),

        # --- 🇬🇧 Vocabulario Inglés ---
        (r"\bWater\b", "agua"),
        (r"\bSugar\b", "azúcar"),
        (r"\bSalt\b", "sal"),
        (r"\bGarlic\b", "ajo"),
        (r"\bOnions\b", "cebollas"),
        (r"\bOnion\b", "cebolla"),
        (r"\bOil\b", "aceite"),
        (r"\bVinegar\b", "vinagre"),
        (r"\bCheese\b", "queso"),
        (r"\bPickled\b", "encurtido"),
        (r"\bFermented\b", "fermentado"),
        (r"\bSauce\b", "salsa"),
        (r"\bBrewed\b", "elaborado"),
        (r"\bYogurt\b", "yogur"),
        (r"\bYoghurt\b", "yogur"),
        (r"\bCider\b", "sidra"),
        (r"\bYeast\b", "levadura"),
        (r"\bPaste\b", "pasta"),
    ]

    for pid, orig_name, desc, source in products:
        new_name = orig_name.strip()
        new_desc = desc if desc else ""
        modified = False

        for pat, repl in translations:
            if re.search(pat, new_name, re.IGNORECASE):
                new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE).strip()
                modified = True

            if new_desc and re.search(pat, new_desc, re.IGNORECASE):
                new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE).strip()
                modified = True

        new_name = re.sub(r"\s+", " ", new_name).strip()

        if modified and len(new_name) > 1:
            cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (new_name, pid))
            conflict = cursor.fetchone()
            if conflict:
                candidate_name = f"{new_name} #{pid}"
                cursor.execute("SELECT id FROM products WHERE name = ? AND id != ?", (candidate_name, pid))
                if cursor.fetchone():
                    candidate_name = f"{new_name} ({source} #{pid})"
                new_name = candidate_name

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
    print(f"\n🎉 Traducción universal masiva completada: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    master_translate()
