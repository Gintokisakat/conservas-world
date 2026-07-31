"""
Script de auditoría CERO TOLERANCIA para revisar exhaustivamente cada palabra
de cada producto en `data/build.db`.
"""

import sqlite3
import re

def zero_tolerance_audit():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method, substrate FROM products")
    products = cursor.fetchall()

    # Patrón de palabras comunes no españolas en alimentos e ingredientes
    foreign_pattern = re.compile(
        r"\b("
        r"water|sugar|salt|garlic|onion|onions|oil|vinegar|cheese|pickled|fermented|sauce|brewed|yogurt|yoghurt|cider|yeast|paste|fillets|smoked|chilli|mustard|cabbage|rice|bean|beans|milk|organic|fresh|sweet|hot|red|green|black|white|style|flavour|flavor|sliced|whole|peeled|diced|chopped|"
        r"eau|sucre|sel|vinaigre|oignon|oignons|ail|huile|moutarde|lait|levure|poivre|piment|chou|carotte|jus|farine|blé|viande|porc|gras|fruits|pomme|poire|citron|bocal|pne|garnie|recette|"
        r"wasser|zucker|essig|säure|salz|milch|hefe|bohnen|kartoffel|speisesalz|senf|zwiebel|zwiebeln|knoblauch|reis|öl|korn|sauerkraut|brot|"
        r"acqua|zucchero|sale|aglio|cipolla|cipolle|pomodoro|aceto|formaggio|olio|latte|lievito|capperi|filetti|sott'olio|"
        r"água|açúcar|alho|cebola|azeite|queijo|leite|morango|amido|sumo|láticos|desnatado|zout|azijn|knoflook|melk|gist|bloem|schimmel|gefermenteerd"
        r")\b",
        re.IGNORECASE
    )

    flagged = []

    for pid, name, desc, method, sub in products:
        text = f"{name} {desc or ''} {method or ''} {sub or ''}"
        matches = foreign_pattern.findall(text)
        if matches:
            unique_matches = list(set([m.lower() for m in matches]))
            flagged.append((pid, name, desc, unique_matches))

    conn.close()

    print(f"🔬 AUDITORÍA CERO TOLERANCIA SOBRE {len(products)} PRODUCTOS:")
    print(f"⚠️ Se encontraron {len(flagged)} productos con palabras no españolas identificadas.")

    if flagged:
        print("\n--- Muestra de los primeros 15 productos detectados ---")
        for pid, name, desc, m in flagged[:15]:
            print(f"  • [{pid}] \"{name}\"")
            print(f"    Palabras no españolas: {m}")
            if desc:
                print(f"    Desc: {desc[:120]}...")
            print()

    return len(flagged)

if __name__ == "__main__":
    zero_tolerance_audit()
