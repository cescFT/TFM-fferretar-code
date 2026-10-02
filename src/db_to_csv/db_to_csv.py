"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

import sqlite3
import pandas as pd
import json
from utils.utils import (
    get_path_sqlite_db,
    get_path_product_csv_from_db,
    get_path_categories_aggregation_csv_from_db,
    get_path_of_data_to_send_to_external_team
)

def extract_json_key(val: str, key: str) -> str|None:
    """
    Function to extract only a specific key from a JSON string.

    Args:
        val (str): The JSON string from which to extract the key.
        key (str): The key to extract from the JSON string.

    Returns:
        str|None: The value associated with the key, or None if the key is not found or the input is invalid.
    """

    if pd.notna(val) and val:
        try:
            return json.loads(val).get(key)
        except (json.JSONDecodeError, TypeError):
            return None
    return None

if __name__ == "__main__":
    print("Script start.")

    db_path = get_path_sqlite_db()
    csv_path = get_path_product_csv_from_db()
    csv_path_aggregation = get_path_categories_aggregation_csv_from_db()
    csv_path_external_team = get_path_of_data_to_send_to_external_team()

    with sqlite3.connect(db_path) as conn:
        print("Generating CSV file of product data.")
        df = pd.read_sql_query("""
            select *
        from products p
        """, conn)

        df['nutriscore'] = df['nutriscore'].apply(lambda x: extract_json_key(x, 'letter'))
        df['ewo_ultra_processed_punctuation'] = df['ewo_ultra_processed_punctuation'].apply(
            lambda x: extract_json_key(x, 'qualification'))

        df.to_csv(csv_path, index=False, sep="|", encoding="utf-8")
        print("CSV product data generated.")
        print("Generating CSV file of categories aggregation.")
        df_aggregate = pd.read_sql_query("""
            select * from categories_counter c
        """, conn)

        df_aggregate.to_csv(csv_path_aggregation, index=False, sep="|", encoding="utf-8")
        print("CSV categories aggregation generated.")

        print("Generating data for external team...")
        df_external_team = pd.read_sql_query("""
            SELECT
                p.id_product,p.product_name, p.origin, p.category, p.subcategory,
                p.second_subcategory, p.alcohol_grades, p.ingredients,
                p.ciqual_text_to_search, p.ciqual_id, p.ciqual_text,
                json_extract(p.ewo_ultra_processed_punctuation, '$.qualification') AS ewo_qualification,
                json_extract(p.nutriscore, '$.letter') AS nutriscore_letter,
                COALESCE(certs.certifications, 'No certificat') AS certifications,
                p.planetscore
            FROM products p
            LEFT JOIN (
                SELECT
                    pc.product_id,
                    GROUP_CONCAT(c.certification_name, ', ') AS certifications
                FROM (
                    SELECT DISTINCT product_id, certification_id
                    FROM product_certifications
                ) pc
                JOIN certifications c ON c.id = pc.certification_id
                GROUP BY pc.product_id
            ) certs ON certs.product_id = p.id_product
            group by p.id_product
        ;""", conn)
        df_external_team.to_csv(csv_path_external_team, index=False, sep="|", encoding="utf-8")
        print("CSV data for external team generated.")

    conn.close()

    print("Script end.")
