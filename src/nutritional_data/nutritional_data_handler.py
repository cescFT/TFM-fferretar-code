"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from gemini_integration import connect
from gemini_integration.request import request_gemini

from interact_db import get_data_from_db
from interact_db.get_data_from_db import get_products_without_nutritional_data
from interact_db.update_products_to_db import update_food_found_nutriments
from constants.constants_variables import constants_variables_getter
from nutriments_processing.process_response import process_response_from_gemini
from manual_nutritional_processing import nutritional_info
import argparse

LIMIT_PRODUCTS = constants_variables_getter('LIMIT_PRODUCTS_TO_GET_NUTRITIONAL_DATA')
BASIC_NUTRIENTS_TO_GET = constants_variables_getter('BASIC_NUTRIENTS_TO_GET')
CERTIFICATIONS_BASIC = constants_variables_getter('CERTIFICATIONS_BASIC')
NO_CERTIFICATIONS = CERTIFICATIONS_BASIC[0]
NO_DATA = BASIC_NUTRIENTS_TO_GET[0]
ENERGY_KCAL = BASIC_NUTRIENTS_TO_GET[1]
ENERGY_KJ = BASIC_NUTRIENTS_TO_GET[2]

def nutritional_data_handler() -> None:
    """
    Function that executes script to get nutritional data for each product.

    Args:
        None.

    Returns:
        None.
    """

    parser = argparse.ArgumentParser(
        description="Nutritional data handler"
    )

    parser.add_argument(
        "-manual",
        type=bool,
        help="Retrieve data manual"
    )

    parser.add_argument(
        "-limit",
        type=int,
        help="Limit items if manual"
    )

    args = parser.parse_args()

    if args.manual:
        if args.limit:
            limit = args.limit
        else:
            limit = 15
    else:
        limit = int(LIMIT_PRODUCTS)


    products_data = get_products_without_nutritional_data(limit)
    print(f"Found {len(products_data)} products without no nutritional data.")

    if not products_data:
        print("Process ended.")
        return

    if not args.manual:
        print("Establishing connection with gemini...")
        gemini_connection = connect.create_connection_to_gemini()
        print("Connection with gemini already done.")
        print("Sending petitions to gemini...")
        nutritional_data_responses = request_gemini(gemini_connection, products_data)
    else:
        nutritional_data_responses = nutritional_info.get_manual_data_from_foods(products_data)

    nutriments = get_data_from_db.get_types_of_nutriments(BASIC_NUTRIENTS_TO_GET)
    certifications = get_data_from_db.get_types_of_certifications(CERTIFICATIONS_BASIC)

    print("Processing responses of gemini...")
    nutriments_to_save = process_response_from_gemini(
        products_data,
        nutritional_data_responses,
        NO_DATA,
        ENERGY_KCAL,
        ENERGY_KJ,
        nutriments,
        NO_CERTIFICATIONS,
        certifications
    )

    print("Saving nutritional data into database...")
    update_food_found_nutriments(nutriments_to_save)
    print("Nutritional data saved correctly into database.")

if __name__ == '__main__':
    print("Starting script...")
    nutritional_data_handler()
    print("End of script.")

