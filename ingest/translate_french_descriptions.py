"""
Script de traducción completa de descripciones en francés e HTML entities al español.
Para Conservas del Mundo (`data/build.db`).
"""

import html
import re
import sqlite3


def translate_french_descriptions():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()
    print(f"📦 Traduciendo descripciones de {len(products)} productos...")

    cleaned_count = 0

    fr_dict = [
        # HTML entities
        (r"&quot;", '"'),
        (r"&amp;", '&'),
        (r"&lt;", '<'),
        (r"&gt;", '>'),
        (r"&#39;", "'"),

        # Fracciones de empaque en títulos
        (r"^1/6\s+", ""),
        (r"^1/4\s+", ""),
        (r"^1/2\s+", ""),

        # Vocabulario de ingredientes en Francés
        (r"\bIngrédients\s*:\s*", "Ingredientes: "),
        (r"\bIngrédients\b", "Ingredientes"),
        (r"\bCornichons français\b", "Pepinillos franceses"),
        (r"\bCornichons\b", "Pepinillos"),
        (r"\bSardines fraîches\b", "Sardinas frescas"),
        (r"\bSardines\b", "Sardinas"),
        (r"\bhuile d'olive vierge extra\b", "aceite de oliva virgen extra"),
        (r"\bhuile d'olive\b", "aceite de oliva"),
        (r"\bhuile de tournesol\b", "aceite de girasol"),
        (r"\bsel marin de l'île de Ré\b", "sal marina de la isla de Ré"),
        (r"\bsel marin\b", "sal marina"),
        (r"\bvinaigre d'alcool\b", "vinagre de alcohol"),
        (r"\bvinaigre de vin blanc\b", "vinagre de vino blanco"),
        (r"\bvinaigre de vin\b", "vinagre de vino"),
        (r"\bvinaigre de table\b", "vinagre de mesa"),
        (r"\bvinaigre\b", "vinagre"),
        (r"\bgraines de moutarde jaunes et noire\b", "semillas de mostaza amarilla y negra"),
        (r"\bgraines de moutarde\b", "semillas de mostaza"),
        (r"\bgraines de coriandre\b", "semillas de cilantro"),
        (r"\bpoivron rouge\b", "pimiento rojo"),
        (r"\boignons blancs\b", "cebollas blancas"),
        (r"\boignons\b", "cebollas"),
        (r"\boignon\b", "cebolla"),
        (r"\baneth\b", "eneldo"),
        (r"\bestragon\b", "estragón"),
        (r"\bépices\b", "especias"),
        (r"\barôme naturel d'estragon avec\b", "aroma natural de estragón con"),
        (r"\barôme naturel\b", "aroma natural"),
        (r"\barômes\b", "aromas"),
        (r"\barôme\b", "aroma"),
        (r"\bLégumes lactofermentés\b", "Vegetales lactofermentados"),
        (r"\bLégumes\b", "Vegetales"),
        (r"\bchou blanc\b", "repollo blanco"),
        (r"\bcarotte lactofermentée\b", "zanahoria lactofermentada"),
        (r"\bcarotte\b", "zanahoria"),
        (r"\bail\b", "ajo"),
        (r"\bplantes aromatiques\b", "plantas aromáticas"),
        (r"\bantioxydant\s*:\s*acide ascorbique\b", "antioxidante: ácido ascórbico"),
        (r"\bcontient des sulfites\b", "contiene sulfitos"),
        (r"\bcontient sulfites\b", "contiene sulfitos"),
        (r"\bdont sulfites\b", "incluyendo sulfitos"),
        (r"\bdont SULFITES\b", "incluyendo sulfitos"),
        (r"\bdont\b", "incluyendo"),
        (r"\beau\b", "agua"),
        (r"\bsucre\b", "azúcar"),
        (r"\bsel\b", "sal"),
    ]

    for pid, name, desc, _source in products:
        new_name = html.unescape(name.strip())
        new_desc = html.unescape(desc) if desc else ""
        modified = False

        # Apply fraction cleanups
        if re.search(r"^1/[2468]\s+", new_name):
            new_name = re.sub(r"^1/[2468]\s+", "", new_name).strip()
            modified = True

        if new_desc:
            for pat, repl in fr_dict:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

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
    print(f"\n🎉 Traducción de descripciones completada: {cleaned_count} productos actualizados.")

if __name__ == "__main__":
    translate_french_descriptions()
