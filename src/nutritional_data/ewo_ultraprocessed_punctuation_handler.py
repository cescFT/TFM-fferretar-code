"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from dto.product_nutritional_data import ProductNutrimentsDTO
from grocery_scraper.constants.constants_variables import constants_variables_getter
from grocery_scraper.utils.utils import get_path_ewo_ingredients_data
from nutritional_data.interact_db.get_data_from_db import get_products_without_ewo_ultraprocessed_qualification
from nutritional_data.ewo.calculate_ultraprocessed_punctuation import calculate_ultraprocessed_punctuation
from nutritional_data.interact_db.update_products_to_db import update_ewo_ultraprocessed_qualification
import argparse
import pandas as pd
import unicodedata

LIMIT_PRODUCTS = constants_variables_getter("LIMIT_PRODUCTS_TO_CALCULATE_ULTRAPROCESSED_PUNCTUATION")

def execute() -> None:
    """
    Main function to calculate EWÖ ultra processed punctuation for products.

    Args:
        None.

    Returns:
        None.
    """

    try:
        excel_path = get_path_ewo_ingredients_data()
        ewo_ingredients = pd.read_excel(excel_path)
    except FileNotFoundError:
        print("EWO ingredients file not found. Please, contact with EWÖ and make an agreement for this data.")
        return

    parser = argparse.ArgumentParser(
        description="Ewö ultra processed punctuation calculator"
    )

    parser.add_argument(
        "-limit",
        type=int,
        help="Limit items"
    )

    args = parser.parse_args()

    limit = int(LIMIT_PRODUCTS)
    if args.limit:
        limit = args.limit

    products = get_products_without_ewo_ultraprocessed_qualification(limit)

    if not products:
        print("No products to calculate ultraprocessed punctuation.")
        return

    ewo_ingredients = prepare_ingredients_df_to_be_processed(ewo_ingredients)

    ultraprocessed_punctuations = {}
    product: ProductNutrimentsDTO
    for product in products:
        punctuation = calculate_ultraprocessed_punctuation(product, ewo_ingredients)
        ultraprocessed_punctuations[product.get_grocery_id()] = punctuation
        print("=" * 20)
        print("\n")

    print("Updating qualifications for products...")
    update_ewo_ultraprocessed_qualification(ultraprocessed_punctuations)
    print("Qualifications updated correctly.")

def prepare_ingredients_df_to_be_processed(ewo_ingredients_information: pd.DataFrame) -> pd.DataFrame:
    """
    Function that prepares information readed from excel to process.
    Args:
        ewo_ingredients_information (pd.DataFrame): Information readed from excel.

    Returns:
        pd.DataFrame: Information prepared to process.
    """

    ewo_ingredients = ewo_ingredients_information[
        ewo_ingredients_information['es'].notna() &
        (ewo_ingredients_information['es'].str.strip() != '')
        ].copy()

    ewo_ingredients['es'] = ewo_ingredients['es'].str.lower()
    ewo_ingredients['es'] = ewo_ingredients['es'].apply(lambda text : ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ))

    ewo_ingredients['reference'] = (
        ewo_ingredients['reference']
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r'^e', 'e-', regex=True)
    )

    ewo_ingredients['sugar'] = ewo_ingredients['sugar'].fillna(False)
    ewo_ingredients['sugar'] = ewo_ingredients['sugar'].replace("true", True)
    ewo_ingredients['sugar'] = ewo_ingredients['sugar'].astype(bool)

    return ewo_ingredients


if __name__ == "__main__":
    print("Script start.")
    execute()
    print("Script end.")
