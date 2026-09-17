"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

import sqlite3
import pandas as pd
from utils.utils import (
    get_path_sqlite_db,
    get_path_product_csv_from_db,
    get_path_categories_aggregation_csv_from_db
)

if __name__ == "__main__":
    print("Script start.")

    db_path = get_path_sqlite_db()
    csv_path = get_path_product_csv_from_db()
    csv_path_aggregation = get_path_categories_aggregation_csv_from_db()

    with sqlite3.connect(db_path) as conn:
        print("Generating CSV file of product data.")
        df = pd.read_sql_query("""
            select *
        from products p
        """, conn)
        df.to_csv(csv_path, index=False, sep="|", encoding="utf-8")
        print("CSV product data generated.")
        print("Generating CSV file of categories aggregation.")
        df_aggregate = pd.read_sql_query("""
            select * from categories_counter c
        """, conn)

        df_aggregate.to_csv(csv_path_aggregation, index=False, sep="|", encoding="utf-8")
        print("CSV categories aggregation generated.")

    conn.close()

    print("Script end.")
