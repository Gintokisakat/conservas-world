"""
Script de auditoría exhaustiva para detectar cualquier producto o descripción en idiomas extranjeros
(Alemán, Italiano, Polaco, Portugués, Francés, Inglés, etc.) en `data/build.db`.
"""

import re
import sqlite3


def audit():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()

    german_matches = []
    italian_matches = []
    polish_matches = []
    english_matches = []
    french_matches = []

    # Patrones por idioma
    de_pat = r"\b(Wasser|Zucker|Essig|Säure|Zwiebeln|Knoblauch|Bohnen|Speisesalz|Senfsaat|Senfkörner|Gurken|Zitronensäure|Gewürze|Milchsäure|Hefe|Kartoffelstärke)\b"
    it_pat = r"\b(Acqua|Zucchero|Aglio|Cipolla|Pomodoro|Aceto|Formaggio|Olio|Latte|Lievito)\b"
    pl_pat = r"\b(Woda|Cukier|Czosnek|Ocet|Ogórki|Kapusta|Sól|Smarowy|Chleb)\b"
    en_pat = r"\b(Water|Sugar|Salt|Garlic|Onion|Oil|Vinegar|Cheese|Pickled|Fermented|Sauce|Brewed|Yogurt|Cider|Yeast|Paste)\b"
    fr_pat = r"\b(Eau|Sucre|Sel|Vinaigre|Oignon|Ail|Huile|Moutarde|Lait|Levure|Poivre|Piment)\b"

    for pid, name, desc, _source in products:
        full_text = f"{name} {desc if desc else ''}"
        
        if re.search(de_pat, full_text, re.IGNORECASE):
            german_matches.append((pid, name, desc))
        elif re.search(it_pat, full_text, re.IGNORECASE):
            italian_matches.append((pid, name, desc))
        elif re.search(pl_pat, full_text, re.IGNORECASE):
            polish_matches.append((pid, name, desc))
        elif re.search(en_pat, full_text, re.IGNORECASE):
            english_matches.append((pid, name, desc))
        elif re.search(fr_pat, full_text, re.IGNORECASE):
            french_matches.append((pid, name, desc))

    conn.close()

    print(f"📊 Resultados de la auditoría sobre {len(products)} productos:")
    print(f"  - Registros con vocabulario en Alemán: {len(german_matches)}")
    print(f"  - Registros con vocabulario en Italiano: {len(italian_matches)}")
    print(f"  - Registros con vocabulario en Polaco: {len(polish_matches)}")
    print(f"  - Registros con vocabulario en Francés: {len(french_matches)}")
    print(f"  - Registros con vocabulario en Inglés: {len(english_matches)}")

    print("\n--- Muestras de Alemán ---")
    for m in german_matches[:5]:
        print(f"  [{m[0]}] {m[1]} -> {m[2][:100] if m[2] else ''}")

    print("\n--- Muestras de Italiano ---")
    for m in italian_matches[:5]:
        print(f"  [{m[0]}] {m[1]} -> {m[2][:100] if m[2] else ''}")

    print("\n--- Muestras de Polaco ---")
    for m in polish_matches[:5]:
        print(f"  [{m[0]}] {m[1]} -> {m[2][:100] if m[2] else ''}")

    print("\n--- Muestras de Inglés ---")
    for m in english_matches[:5]:
        print(f"  [{m[0]}] {m[1]} -> {m[2][:100] if m[2] else ''}")

if __name__ == "__main__":
    audit()
