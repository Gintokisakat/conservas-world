"""
Script de traducción completa y exhaustiva para TODOS los idiomas restantes
(Francés, Portugués, Galego, Italiano, Alemán y Holandés) en descripciones y nombres de `data/build.db`.
"""

import sqlite3
import re

def translate_all_languages():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method FROM products")
    products = cursor.fetchall()

    print(f"📦 Procesando traducción multitratamiento en {len(products)} productos...")
    updated_count = 0

    all_lang_map = [
        # --- 🇫🇷 FRANCÉS ---
        (r"\bIngrédients\s*:\s*", "Ingredientes: "),
        (r"\bIngrédients\b", "Ingredientes"),
        (r"\bLégumes lactofermentés\b", "Vegetales lactofermentados"),
        (r"\bLégumes\b", "Vegetales"),
        (r"\bchou blanc\b", "repollo blanco"),
        (r"\bchou\b", "repollo"),
        (r"\bcarotte lactofermentée\b", "zanahoria lactofermentada"),
        (r"\bcarotte\b", "zanahoria"),
        (r"\bcarottes\b", "zanahorias"),
        (r"\boignons blancs\b", "cebollas blancas"),
        (r"\boignons\b", "cebollas"),
        (r"\boignon\b", "cebolla"),
        (r"\bail\b", "ajo"),
        (r"\beau\b", "agua"),
        (r"\bsucre\b", "azúcar"),
        (r"\bsel marin\b", "sal marina"),
        (r"\bsel\b", "sal"),
        (r"\bvinaigre d'alcool\b", "vinagre de alcohol"),
        (r"\bvinaigre de vin\b", "vinagre de vino"),
        (r"\bvinaigre\b", "vinagre"),
        (r"\bhuile d'olive virgen extra\b", "aceite de oliva virgen extra"),
        (r"\bhuile d'olive\b", "aceite de oliva"),
        (r"\bhuile de tournesol\b", "aceite de girasol"),
        (r"\bhuile\b", "aceite"),
        (r"\bmoutarde\b", "mostaza"),
        (r"\blait\b", "leche"),
        (r"\blevure\b", "levadura"),
        (r"\bpoivre\b", "pimienta"),
        (r"\bpiment\b", "chile / pimentón"),
        (r"\bjus de citron\b", "zumo de limón"),
        (r"\bjus\b", "jugo / zumo"),
        (r"\bfarine de blé\b", "harina de trigo"),
        (r"\bfarine\b", "harina"),
        (r"\bblé\b", "trigo"),
        (r"\bviande de porc\b", "carne de cerdo"),
        (r"\bviande\b", "carne"),
        (r"\bporc\b", "cerdo"),
        (r"\bgras\b", "grasa"),
        (r"\bfruits rouges\b", "frutos rojos"),
        (r"\bfruits\b", "frutas"),
        (r"\bpomme\b", "manzana"),
        (r"\bpoire\b", "pera"),
        (r"\bcitron\b", "limón"),

        # --- 🇵🇹 PORTUGUÉS / GALEGO ---
        (r"\bIngredientes\s*:\s*", "Ingredientes: "),
        (r"\bLeite desnatado\b", "Leche desnatada"),
        (r"\bLeite\b", "Leche"),
        (r"\bleite\b", "leche"),
        (r"\bmorango\b", "fresa"),
        (r"\bamido de milho\b", "almidón de maíz"),
        (r"\bamido\b", "almidón"),
        (r"\bmilho\b", "maíz"),
        (r"\bsumo concentrado de limão\b", "zumo concentrado de limón"),
        (r"\bsumo de limão\b", "zumo de limón"),
        (r"\bsumo\b", "zumo / jugo"),
        (r"\bfermentos láticos\b", "fermentos lácticos"),
        (r"\bláticos\b", "lácticos"),
        (r"\bdesnatado\b", "desnatado"),
        (r"\baçúcar\b", "azúcar"),
        (r"\bágua\b", "agua"),
        (r"\balho\b", "ajo"),
        (r"\bcebola\b", "cebolla"),
        (r"\bazeite de oliva\b", "aceite de oliva"),
        (r"\bazeite\b", "aceite de oliva"),
        (r"\bqueijo\b", "queso"),
        (r"\bfarinha\b", "harina"),

        # --- 🇮🇹 ITALIANO ---
        (r"\bIngredienti\s*:\s*", "Ingredientes: "),
        (r"\bAcqua\b", "Agua"),
        (r"\bacqua\b", "agua"),
        (r"\bZucchero\b", "Azúcar"),
        (r"\bzucchero\b", "azúcar"),
        (r"\bSale\b", "Sal"),
        (r"\bsale\b", "sal"),
        (r"\bAglio\b", "Ajo"),
        (r"\baglio\b", "ajo"),
        (r"\bCipolla\b", "Cebolla"),
        (r"\bcipolla\b", "cebolla"),
        (r"\bcipolle\b", "cebollas"),
        (r"\bPomodoro\b", "Tomate"),
        (r"\bpomodoro\b", "tomate"),
        (r"\bAceto di mele\b", "vinagre de manzana"),
        (r"\baceto\b", "vinagre"),
        (r"\bFormaggio\b", "Queso"),
        (r"\bformaggio\b", "queso"),
        (r"\bOlio d'oliva\b", "aceite de oliva"),
        (r"\bolio di semi di girasole\b", "aceite de girasol"),
        (r"\bolio di oliva\b", "aceite de oliva"),
        (r"\bolio\b", "aceite"),
        (r"\bLatte\b", "Leche"),
        (r"\blatte\b", "leche"),
        (r"\bLievito\b", "Levadura"),
        (r"\blievito\b", "levadura"),

        # --- 🇩🇪 ALEMÁN ---
        (r"\bZutaten\s*:\s*", "Ingredientes: "),
        (r"\bWasser\b", "agua"),
        (r"\bTrinkwasser\b", "agua potable"),
        (r"\bZucker\b", "azúcar"),
        (r"\bEssig\b", "vinagre"),
        (r"\bSäure\b", "ácido"),
        (r"\bSalz\b", "sal"),
        (r"\bSpeisesalz\b", "sal"),
        (r"\bMeersalz\b", "sal marina"),
        (r"\bMilch\b", "leche"),
        (r"\bHefe\b", "levadura"),
        (r"\bBohnen\b", "alubias / frijoles"),
        (r"\bKartoffelstärke\b", "almidón de patata"),
        (r"\bSenf\b", "mostaza"),
        (r"\bZwiebeln\b", "cebollas"),
        (r"\bZwiebel\b", "cebolla"),
        (r"\bKnoblauch\b", "ajo"),

        # --- 🇳🇱 HOLANDÉS ---
        (r"\bIngrediënten\s*:\s*", "Ingredientes: "),
        (r"\bWater\b", "Agua"),
        (r"\bwater\b", "agua"),
        (r"\bSuiker\b", "Azúcar"),
        (r"\bsuiker\b", "azúcar"),
        (r"\bZout\b", "Sal"),
        (r"\bzout\b", "sal"),
        (r"\bAzijn\b", "Vinagre"),
        (r"\bazijn\b", "vinagre"),
        (r"\bUi\b", "Cebolla"),
        (r"\bui\b", "cebolla"),
        (r"\bKnoflook\b", "Ajo"),
        (r"\bknoflook\b", "ajo"),
        (r"\bOlie\b", "Aceite"),
        (r"\bolie\b", "aceite"),
    ]

    for pid, name, desc, method in products:
        new_name = name.strip()
        new_desc = desc if desc else ""
        new_method = method if method else ""
        modified = False

        if new_desc:
            for pat, repl in all_lang_map:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

        if new_name:
            for pat, repl in all_lang_map:
                if re.search(pat, new_name, re.IGNORECASE):
                    new_name = re.sub(pat, repl, new_name, flags=re.IGNORECASE)
                    modified = True

        if modified:
            new_desc = re.sub(r"\s+", " ", new_desc).strip()
            new_name = re.sub(r"\s+", " ", new_name).strip()
            cursor.execute("UPDATE products SET name = ?, description = ? WHERE id = ?", (new_name, new_desc if new_desc else None, pid))
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
    print(f"\n🎉 Traducción multitratamiento completada: {updated_count} productos actualizados.")

if __name__ == "__main__":
    translate_all_languages()
