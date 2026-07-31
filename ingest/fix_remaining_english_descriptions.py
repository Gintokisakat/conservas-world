"""
Script de traducción final y refinamiento gramatical de descripciones en español.
Para Conservas del Mundo (`data/build.db`).
"""

import sqlite3
import re

def fix_remaining():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, method FROM products")
    products = cursor.fetchall()

    print(f"📦 Aplicando pulido final de descripciones en {len(products)} productos...")
    updated_count = 0

    phrases = [
        (r"\bleche producto\b", "producto lácteo"),
        (r"\bThis producto can be\b", "Este producto puede ser"),
        (r"\bcan be\b", "puede ser"),
        (r"\bis elaborado\b", "es elaborado"),
        (r"\bwell known\b", "famoso"),
        (r"\bsplit legumes\b", "legumbres partidas"),
        (r"\bequal parts de\b", "partes iguales de"),
        (r"\bpig head\b", "cabeza de cerdo"),
        (r"\bpopular bebida de\b", "bebida popular de"),
        (r"\bmade en\b", "elaborado a"),
        (r"\bsubproducto of making\b", "subproducto de la elaboración de"),
        (r"\bIt has un\b", "Tiene una"),
        (r"\bIt has\b", "Tiene"),
        (r"\bis el nombre histórico de quesos produced en\b", "es el nombre histórico de los quesos producidos en"),
        (r"\bproduced en\b", "producido en"),
        (r"\brojo moho arroz\b", "arroz de moho rojo"),
        (r"\brojo levadura arroz\b", "arroz de levadura roja"),
        (r"\bdesayuno plato\b", "plato de desayuno"),
        (r"\bconsumido un lo largo de\b", "consumido a lo largo de"),
        (r"\bqueso de textura granulada\b", "queso granulado"),
        (r"\bstirred cuajada queso\b", "queso de cuajada removida"),
        (r"\bIn el state de\b", "En el estado de"),
        (r"\bthe residents produce un\b", "los habitantes producen una"),
        (r"\balcoholic bebida\b", "bebida alcohólica"),
        (r"\bEthiopian queso fresco artesanal\b", "queso fresco artesanal etíope"),
        (r"\bobtenido un partir de\b", "obtenido a partir de"),
        (r"\bsoured leche\b", "leche agria"),
        (r"\bácido láctico fermentado arroz-camarones mezcla\b", "mezcla fermentada de arroz y camarones"),
        (r"\bgenerally\b", "generalmente"),
        (r"\bqueso speciality de\b", "especialidad de queso de"),
        (r"\bwhere Es is\b", "donde es"),
        (r"\bfull-fat leche de oveja\b", "leche entera de oveja"),
        (r"\bThe leche comes de some specific\b", "La leche proviene de algunas especies específicas"),
        (r"\bduro cocinado queso\b", "queso cocido de pasta dura"),
        (r"\bwithout openings\b", "sin aberturas"),
        (r"\bsmeared rind\b", "corteza untada"),
        (r"\bProduced en winter o summer\b", "Producido en invierno o verano"),
        (r"\bsabores are nuanced\b", "los sabores presentan matices"),
        (r"\bvery common turkish brined queso\b", "queso turco en salmuera muy común"),
        (r"\bproducido un partir de\b", "producido a partir de"),
        (r"\bunpasteurized sheep,cow o\b", "oveja, vaca o cabra sin pasteurizar"),
        (r"\bmild alcoholic bebida\b", "bebida alcohólica suave"),
        (r"\bblue-veined queso\b", "queso de vetas azules"),
        (r"\bsimilar para\b", "similar a"),
        (r"\bbut elaborado con\b", "pero elaborado con"),
        (r"\bpasteurized o\b", "pasteurizada o"),
        (r"\buncooked pressed queso\b", "queso prensado no cocido"),
        (r"\bproducido por hand en\b", "producido a mano a"),
        (r"\babove sea level\b", "sobre el nivel del mar"),
        (r"\bun partir de\b", "a partir de"),
        (r"\bun lo largo de\b", "a lo largo de"),
        (r"\bIn el\b", "En el"),
        (r"\bIn la\b", "En la"),
        (r"\bIn los\b", "En los"),
        (r"\bThe proceso\b", "El proceso"),
        (r"\bThe método\b", "El método"),
        (r"\bThe preparación\b", "La preparación"),
        (r"\bThe mezcla\b", "La mezcla"),
        (r"\bThe producto\b", "El producto"),
        (r"\bThe queso\b", "El queso"),
        (r"\bThe leche\b", "La leche"),
        (r"\bThis producto\b", "Este producto"),
        (r"\bThis queso\b", "Este queso"),
        (r"\bare \b", "son "),
        (r"\bis \b", "es "),
        (r"\bwas \b", "fue "),
        (r"\bwere \b", "fueron "),
        (r"\bhas \b", "tiene "),
        (r"\bhave \b", "tienen "),
        (r"\bcan \b", "puede "),
        (r"\bcould \b", "podría "),
        (r"\bshould \b", "debería "),
        (r"\bmust \b", "debe "),
    ]

    for pid, name, desc, method in products:
        new_desc = desc if desc else ""
        new_method = method if method else ""
        modified = False

        if new_desc:
            for pat, repl in phrases:
                if re.search(pat, new_desc, re.IGNORECASE):
                    new_desc = re.sub(pat, repl, new_desc, flags=re.IGNORECASE)
                    modified = True

        if new_method:
            for pat, repl in phrases:
                if re.search(pat, new_method, re.IGNORECASE):
                    new_method = re.sub(pat, repl, new_method, flags=re.IGNORECASE)
                    modified = True

        if modified:
            new_desc = re.sub(r"\s+", " ", new_desc).strip()
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
    print(f"\n🎉 Pulido final de descripciones completado: {updated_count} productos actualizados.")

if __name__ == "__main__":
    fix_remaining()
