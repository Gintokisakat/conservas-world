"""
Script de auditoría ultra-profunda para detectar CUALQUIER texto que no esté en español
en `data/build.db` (nombres, descripciones, métodos, sustratos).
"""

import re
import sqlite3


def deep_audit():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method, substrate FROM products")
    products = cursor.fetchall()

    results = []

    # Diccionario amplio con grupos no capturantes (?:...)
    foreign_words = [
        # Inglés
        r"\b(?:water|sugar|salt|garlic|onion|onions|oil|vinegar|cheese|pickled|fermented|sauce|brewed|yogurt|yoghurt|cider|yeast|paste|fillets|smoked|chilli|mustard|cabbage|rice|bean|beans|milk|organic|fresh|sweet|hot|red|green|black|white|style|flavour|flavor|sliced|whole|peeled|diced|chopped)\b",
        # Francés
        r"\b(?:eau|sucre|sel|vinaigre|oignon|oignons|ail|huile|moutarde|lait|levure|poivre|piment|chou|carotte|jus|farine|blé|viande|porc|gras|fruits|pomme|poire|citron|bocal|pne|garnie|recette)\b",
        # Alemán
        r"\b(?:wasser|zucker|essig|säure|salz|milch|hefe|bohnen|kartoffel|speisesalz|senf|zwiebel|zwiebeln|knoblauch|reis|öl|korn|sauerkraut|brot)\b",
        # Italiano
        r"\b(?:acqua|zucchero|sale|aglio|cipolla|cipolle|pomodoro|aceto|formaggio|olio|latte|lievito|capperi|filetti|sott'olio)\b",
        # Portugués / Holandés / Caracteres no latinos
        r"\b(?:água|açúcar|alho|cebola|azeite|queijo|leite|morango|amido|sumo|láticos|desnatado|zout|azijn|knoflook|melk|gist|bloem|schimmel|gefermenteerd)\b",
        r"[а-яА-Яα-ωΑ-Ω]",
    ]

    combined_regex = re.compile("|".join(foreign_words), re.IGNORECASE)

    for pid, name, desc, method, sub in products:
        full_text = f"{name} {desc or ''} {method or ''} {sub or ''}"
        matches = combined_regex.findall(full_text)
        if matches:
            results.append((pid, name, desc, list(set(matches))[:5]))

    conn.close()

    print(f"📊 Auditoría Ultra-Profunda sobre {len(products)} productos:")
    print(f"❌ Se encontraron {len(results)} productos con posibles términos no españoles.\n")

    for pid, name, desc, matches in results[:30]:
        print(f"  - [{pid}] Título: \"{name}\"")
        print(f"    Coincidencias no españolas: {matches}")
        if desc:
            print(f"    Desc: {desc[:100]}...")
        print()

if __name__ == "__main__":
    deep_audit()
