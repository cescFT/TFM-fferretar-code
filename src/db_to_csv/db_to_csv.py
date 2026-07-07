import pandas as pd
import sqlite3
from utils.utils import get_path_sqlite_db, get_path_csv_from_db

if __name__ == "__main__":
    print("Inici script...")

    db_path = get_path_sqlite_db()
    csv_path = get_path_csv_from_db()

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("""
            select p.*, n.nom as nom_nutrient, pn.quantitat as quantitat_nutrient, n.unitat_mesura_nutrient
        from products p
        left join producte_nutrients pn on pn.producte_mercadona_id = p.id_product
        left join nutrients n on n.id = pn.nutrient_id
        """, conn)
        df.to_csv(csv_path, index=False)

    conn.close()

    print("Fi script.")