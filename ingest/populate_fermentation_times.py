"""
Script para enriquecer fermentation_time y storage_life en los 6,165 productos de data/build.db.
"""

import sqlite3

CATEGORY_DEFAULTS = {
    "fermento_lactico": ("1-3 semanas", "3-6 meses (refrigerado)"),
    "encurtido_fermentado": ("2-4 semanas", "6-12 meses (refrigerado)"),
    "fermento_acetico": ("3-6 semanas", "12-24 meses"),
    "encurtido_vinagre": ("1-2 semanas", "12-24 meses"),
    "fermento_alcoholico": ("1-4 semanas", "6-12 meses"),
    "fermento_koji": ("3-12 meses", "12-24 meses (refrigerado)"),
    "conserva_esterilizada": ("Procesamiento térmico", "12-36 meses (lata/frasco)"),
    "conserva_azucar": ("Cocción con azúcar", "12 meses"),
    "encurtido_salmuera": ("2-4 semanas", "6-12 meses"),
    "ahumado": ("1-3 días (ahumado)", "1-3 meses"),
    "secado": ("3-14 días (deshidratado)", "6-12 meses"),
    "curado_sal": ("1-6 meses", "6-12 meses"),
    "fermento_mixto": ("2-6 semanas", "6-12 meses (refrigerado)"),
    "fermento_alcalino": ("3-7 días", "3-6 meses")
}

DEFAULT_TIME = "1-3 semanas"
DEFAULT_STORAGE = "6-12 meses (refrigerado)"


def populate_times():
    conn = sqlite3.connect("data/build.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, c.code, p.fermentation_time, p.storage_life
        FROM products p
        LEFT JOIN product_category pc ON p.id = pc.product_id
        LEFT JOIN categories c ON pc.category_id = c.id
    """)
    rows = cursor.fetchall()

    updated_time = 0
    updated_storage = 0

    for product_id, cat_code, current_time, current_storage in rows:
        target_time, target_storage = CATEGORY_DEFAULTS.get(cat_code, (DEFAULT_TIME, DEFAULT_STORAGE))

        new_time = current_time if current_time else target_time
        new_storage = current_storage if current_storage else target_storage

        if new_time != current_time or new_storage != current_storage:
            cursor.execute("""
                UPDATE products
                SET fermentation_time = ?, storage_life = ?
                WHERE id = ?
            """, (new_time, new_storage, product_id))
            if not current_time:
                updated_time += 1
            if not current_storage:
                updated_storage += 1

    conn.commit()
    conn.close()

    print("✅ Enriquecimiento completado:")
    print(f"   • Tiempos de fermentación actualizados: {updated_time}")
    print(f"   • Tiempos de conservación actualizados: {updated_storage}")

if __name__ == "__main__":
    populate_times()
