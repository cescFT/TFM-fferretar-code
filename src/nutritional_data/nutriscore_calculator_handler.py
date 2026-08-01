"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from interact_db.get_data_from_db import get_products_without_nutriscore
from constants.constants_variables import constants_variables_getter
from nutriscore.calculate_nutriscore import calculate_nutriscore
from dto.product_nutritional_data import ProductNutrimentsDTO
from interact_db.update_products_to_db import update_nutriscore_from_nutriments
import argparse

LIMIT_PRODUCTS = constants_variables_getter('LIMIT_PRODUCTS_TO_GET_NUTRISCORE')

def execute() -> None:
    """
    Function that executes the script for calculate nutriscore data.

    Args:
        None.

    Returns:
        None.
    """

    parser = argparse.ArgumentParser(
        description="Nustriscore calculator"
    )

    parser.add_argument(
        "-limit",
        type=int,
        help="Limit items"
    )

    args = parser.parse_args()

    if args.limit:
        limit = args.limit
    else:
        limit = int(LIMIT_PRODUCTS)


    products = get_products_without_nutriscore(limit)

    if not products:
        print("All the products has calculated nutriscore!")
        return

    nutriscore_to_save = {}

    product: ProductNutrimentsDTO
    for product in products:
        nutriscore = calculate_nutriscore(product)
        nutriscore_to_save[product.get_mercadona_id()] = nutriscore
        print("="*20)
        print("\n")

    print("Updating nutriscore for products...")
    update_nutriscore_from_nutriments(nutriscore_to_save)
    print("Nustriscore saved correctly!")

if __name__ == '__main__':
    print("Starting script...")
    execute()
    print("End of script.")