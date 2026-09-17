"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from dto.product_scrap_data import ProductScrapedDTO
from mercadona_navigator import product_scrap_data
from mercadona_navigator.initialize_mercadona_grocery import initialize
from validations.validate_postal_code import validate as validate_postal_code
from constants.constants_variables import constants_variables_getter
from mercadona_navigator.navigate_through_main_page import navigate_through_main_page

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dto.product_scrap_data_request import ProductScrapDataRequestDTO
from utils.utils import insert_product_data_to_database, clear_database

import concurrent.futures
import argparse
import time

def execute_scraper() -> None:
    """
    Function that executes scraping into mercadona supermarket.

    Args:
        None.

    Returns:
        None.
    """

    parser = argparse.ArgumentParser(
        description="Mercadona Scraper"
    )

    parser.add_argument(
        "-cp",
        type=str,
        help="Postal Code variable name"
    )

    parser.add_argument(
        "-clear",
        type=bool,
        help="Clear database"
    )

    args = parser.parse_args()

    if args.cp:
        postal_code_data = validate_postal_code(args.cp)
        postal_code = postal_code_data['POSTAL_CODE']
        wh_code = postal_code_data['WH']
    else:
        postal_code_data = constants_variables_getter('MONTFERRI_DATA')
        postal_code = postal_code_data['POSTAL_CODE']
        wh_code = postal_code_data['WH']

    if args.clear:
        clear_database()
        print("Database is cleared.")

    navigator = initialize(postal_code)

    if not navigator:
        raise Exception("No s'ha pogut inicialitzar el navegador. Tancant sraper")

    urls_to_follow = navigate_through_main_page(navigator)

    products_to_scrap_urls = {}
    start_date_total = time.perf_counter()
    for title, url in urls_to_follow.items():
        start_date = time.perf_counter()
        navigator.get(url)
        products_to_scrap_urls[title] = []

        print(f"Getting product urls of {title} - {url}")

        element_h2 = WebDriverWait(navigator, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2.section__header.headline1-b"))
        )

        title_text = element_h2.text
        print(f"Extracted title is: {title_text}")

        products = WebDriverWait(navigator, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-cell-container"))
        )

        position = 1
        for product in products:
            products_to_scrap_urls_result = product_scrap_data.get_urls_and_data_from_specific_page(
                product, navigator, position, title_text
            )
            position += 1

            if products_to_scrap_urls_result:
                products_to_scrap_urls[title].append(products_to_scrap_urls_result)

            if position % 10 == 0:
                time.sleep(3)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_date
        print(f"Total products of {title}: {len(products_to_scrap_urls[title])}. Execution time {elapsed_time:.2f} seconds.")
        #break # comentar aquesta linia quan funcioni per tots els elements...
    navigator.quit()

    end_time_total = time.perf_counter()
    print(f"Total time for all principal categories: {((end_time_total - start_date_total)/60):.2f} min.")

    info_products = []
    products_to_process = []
    for title, product_data in products_to_scrap_urls.items():
        for product_data_item in product_data:
            product_scrap_data_request = ProductScrapDataRequestDTO(
                product_data_item, title, wh_code
            )
            products_to_process.append(product_scrap_data_request)

    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        resultats = executor.map(product_scrap_data.process_thread_product_scrap_data, products_to_process)

        product_info: ProductScrapedDTO
        for product_info in resultats:
            if product_info:
                info_products.append(product_info)
                print(f"Product {product_info.get_product_name()} processed correctly")

    print(f"Total products obtained in this scraper execution: {len(info_products)}")
    print("Inserting products into database...")
    insert_product_data_to_database(info_products)
    print("Products inserted correctly into database.")

if __name__ == "__main__":
    print("Initializing scraper...")
    execute_scraper()
    print("End of scraper.")