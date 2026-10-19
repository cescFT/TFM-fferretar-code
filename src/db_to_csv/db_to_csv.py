"""
TFM: The healthiness and sustainability of food promotions in a Spanish online supermarket

Author: Francesc Ferré Tarrés
"""

import sqlite3
import pandas as pd
import json

from dto.product_nutritional_data import ProductNutrimentsDTO
from utils.factory.product_nutriments_factory import create_from_product_id
from utils.utils import (
    get_path_sqlite_db,
    get_path_product_csv_from_db,
    get_path_categories_aggregation_csv_from_db,
    get_path_of_data_to_send_to_external_team
)

from nutriscore.parse_grocery_category_to_nutriscore_category import parse as parse_grocery_cat_to_nutriscore_cat

def check_if_nutriscore_can_be_calculated(product: ProductNutrimentsDTO) -> str:
    """
    Function to check if product can be calculated nutriscore.
    Args:
        product (ProductNutrimentsDTO): product dto.

    Returns:
        str: String with the information about if nutriscore can not be calculated.
    """

    if not product.get_nutriments():
        return "NO_NUTRIMENTS"

    category = parse_grocery_cat_to_nutriscore_cat(product)

    if not category:
        return "NOT_NUTRISCORE_CATEGORY"

    if category == "HAS_ALCOHOL":
        return "HAS_ALCOHOL"

    return ""

def check_if_ewo_ultraprocessed_level_can_be_calculated(product: ProductNutrimentsDTO) -> str:
    """
    Function to check if product can be calculated ewo ultraprocessing level.
    Args:
        product (ProductNutrimentsDTO): product dto.

    Returns:
        str: String with the information about if ewo ultraprocessing level can not be calculated.
    """

    if product.get_alcohol_grades():
        return "HAS_ALCOHOL"

    return ""

def generate_csv_product_data_for_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auxiliary function to generate csv product data for analysis.
    Args:
        df (pd.DataFrame): dataframe with the product data.

    Returns:
        pd.DataFrame: dataframe with the product data for analysis.
    """

    df['nutriscore'] = df['nutriscore'].apply(lambda x: extract_json_key(x, 'letter'))
    df['ewo_ultra_processed_punctuation'] = df['ewo_ultra_processed_punctuation'].apply(
        lambda x: extract_json_key(x, 'qualification'))

    print("Preparing data to check if nutriscore and ewo can be calculated")
    product_dtos = {}
    print("Creating product DTOs")
    id_products = df['id_product'].unique()
    id_product_idx = 1
    for id in id_products:
        product_dto: ProductNutrimentsDTO
        product_dto = create_from_product_id(id)
        product_dtos[product_dto.get_grocery_id()] = product_dto
        print(f"DTO product {id_product_idx} of {len(id_products)} created.", flush=True)
        id_product_idx += 1

    print("Checking if nutriscore and ewo can be calculated")
    nutri_score_be_calculated = {}
    ewo_be_calculated = {}
    for product_dto in product_dtos.values():
        can_nutriscore_be_calculated = check_if_nutriscore_can_be_calculated(product_dto)
        can_ewo_be_calculated = check_if_ewo_ultraprocessed_level_can_be_calculated(product_dto)
        nutri_score_be_calculated[product_dto.get_grocery_id()] = can_nutriscore_be_calculated
        ewo_be_calculated[product_dto.get_grocery_id()] = can_ewo_be_calculated

    df["can_nutriscore_be_calculated"] = (
        df["id_product"].map(nutri_score_be_calculated)
    )

    df["can_ewo_be_calculated"] = (
        df["id_product"].map(ewo_be_calculated)
    )
    print("CSV product data ready to be generated.")
    return df

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

        df = generate_csv_product_data_for_analysis(df)
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
