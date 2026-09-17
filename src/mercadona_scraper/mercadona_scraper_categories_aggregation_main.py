"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""
from dto.categories_aggregate import CategoriesAggregate
from mercadona_scraper.constants.constants_variables import constants_variables_getter
from validations.validate_postal_code import validate as validate_postal_code
from mercadona_navigator.initialize_mercadona_grocery import initialize
from mercadona_scraper.mercadona_navigator.navigate_through_categories import (
    obtain_valid_urls_to_follow, calculate_items_available_to_be_sold
)

from utils.utils import insert_aggregate_data_into_db
import argparse

BASIC_URL_CATEGORIES = constants_variables_getter("BASIC_URL_CATEGORIES")

def execute() -> None:
    """
    Main execution to calculate the total products per categories and subcategories.

    Args:
        None.

    Returns:
        None.
    """

    parser = argparse.ArgumentParser(
        description="Mercadona Scraper aggregation total products per categories and subcategories"
    )

    parser.add_argument(
        "-cp",
        type=str,
        help="Postal Code variable name"
    )

    args = parser.parse_args()

    if args.cp:
        postal_code_data = validate_postal_code(args.cp)
        postal_code = postal_code_data['POSTAL_CODE']
    else:
        postal_code_data = constants_variables_getter('MONTFERRI_DATA')
        postal_code = postal_code_data['POSTAL_CODE']

    navigator = initialize(postal_code, False, BASIC_URL_CATEGORIES)

    if not navigator:
        raise Exception("No s'ha pogut inicialitzar el navegador. Tancant sraper")

    urls_to_follow = obtain_valid_urls_to_follow(navigator)

    print(f"Total urls to be scraped: {len(urls_to_follow)}")

    to_save = []
    for url_data in urls_to_follow:
        category = url_data['category']
        subcategory = url_data['subcategory']
        print(f"Calculating category {category} and subcategory {subcategory}")
        total_items = calculate_items_available_to_be_sold(navigator,url_data['url'])

        to_save.append(CategoriesAggregate(
                category=category,subcategory=subcategory,
                total_items=total_items,postal_code=postal_code
            )
        )
        print(f"Total items: {total_items}")

    print("Establishing database connection to save aggregation data.")
    insert_aggregate_data_into_db(to_save)
    print("Aggregation data saved successfully.")

if __name__ == "__main__":
    print("Script start.")
    execute()
    print("Script end.")
