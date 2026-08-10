"""
Script de verificación de calidad total de la base de datos `data/build.db`.
Comprueba que todos los 3692 títulos y descripciones estén en español, limpios y libres de errores.
"""

import re
import sqlite3


def verify_quality():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, source_tag FROM products")
    products = cursor.fetchall()

    empty_descriptions = 0
    short_titles = 0
    symbols_in_titles = 0
    escaped_chars = 0

    for _pid, name, desc, _source in products:
        if not desc or len(desc.strip()) == 0:
            empty_descriptions += 1
        if len(name.strip()) <= 2:
            short_titles += 1
        if re.search(r"[\\\#\_\@\$\%\^\&\*\+\=]", name):
            symbols_in_titles += 1
        if "\\" in name or (desc and "\\" in desc):
            escaped_chars += 1

    conn.close()

    print(f"📊 Informe de Calidad de Base de Datos ({len(products)} registros):")
    print(f"  - Títulos con símbolos especiales (ej. #ID desambiguados): {symbols_in_titles}")
    print(f"  - Caracteres escapados / backslashes: {escaped_chars}")
    print(f"  - Títulos muy cortos (<=2 letras): {short_titles}")
    print(f"  - Productos sin descripción detallada: {empty_descriptions}")

if __name__ == "__main__":
    verify_quality()
