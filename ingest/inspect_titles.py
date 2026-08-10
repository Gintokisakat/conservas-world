import re
import sqlite3

conn = sqlite3.connect("data/build.db")
cursor = conn.cursor()

cursor.execute("SELECT id, name, description, source_tag FROM products")
products = cursor.fetchall()

broken = []
foreign_scripts = []
non_es = []

es_words = r"\b(de|del|la|el|las|los|con|en|y|para|al|por|sin|queso|salsa|vinagre|mermelada|cebolla|pepinillos|chucrut|cerveza|pan|leche|aceite|harina|pescado|soja|fermentado|conserva|encurtido|jamón|salmuera)\b"

for pid, name, _desc, source in products:
    if "\\" in name or "'" in name or "&" in name or ";" in name or "  " in name or name != name.strip():
        broken.append((pid, name, source))
    
    if re.search(r"[\u0400-\u04FF\u4E00-\u9FFF\u3040-\u30FF\uac00-\ud7af\u0e00-\u0e7f\u0600-\u06FF\u0370-\u03FF]", name):
        foreign_scripts.append((pid, name, source))
    elif not re.search(es_words, name, re.IGNORECASE) and len(name.split()) >= 2:
        non_es.append((pid, name, source))

print(f"1. Nombres con caracteres rotos/escapados/html: {len(broken)}")
for p in broken[:25]:
    print(f"  - [{p[0]}] {p[1]} ({p[2]})")

print(f"\n2. Nombres con escrituras extranjeras (Cirílico/Chino/Japonés/Thai...): {len(foreign_scripts)}")
for p in foreign_scripts[:25]:
    print(f"  - [{p[0]}] {p[1]} ({p[2]})")

print(f"\n3. Nombres en otros idiomas o sin términos españoles (Total: {len(non_es)}):")
for p in non_es[:30]:
    print(f"  - [{p[0]}] {p[1]} ({p[2]})")
