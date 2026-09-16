"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from constants.constants_variables import constants_variables_getter
from pathlib import Path

from dto.product_nutritional_data import ProductNutrimentsDTO
from dto.product_scrap_data import ProductScrapedDTO

import sqlite3


def accept_cookies(driver: webdriver.Chrome) -> None:
    """
    Function that enables accept cookies in Mercadona's supermarket online.

    Args:
        driver (webdriver.Chrome): Chrome driver.

    Returns:
        None.
    """

    try:
        boto_cookies = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//button[contains(text(), 'Aceptar')] | //button[@data-testid='cookie-policy-accept']"))
        )
        boto_cookies.click()
        print("Accepted cookies.")
    except Exception:
        print("Cookies panel has not appear or is closed automatically.")

def process_postal_code(driver:webdriver.Chrome, postal_code: str) -> None:
    """
    Function responsible for processing postal code and submit form.

    Args:
        driver (webdriver.Chrome): Chrome driver.
        postal_code (str): Postal code.

    Returns:
         None.
    """

    print(f"Introducing postal code: {postal_code}...")
    input_cp = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "postalCode"))
    )
    input_cp.clear()
    input_cp.send_keys(postal_code)

    input_cp.send_keys(Keys.RETURN)

def get_postal_code_from_wh_id(wh_id: str) -> str:
    """
    Function that retrieve postal code from warehouse id.

    Args:
        wh_id (str): warehouse id.

    Returns:
        str: postal code.
    """

    constants_name = [
        "BCN_DATA",
        "MONTFERRI_DATA"
    ]

    for constant in constants_name:
        city_data = constants_variables_getter(constant)
        if city_data['WH'] == wh_id:
            return city_data['POSTAL_CODE']

    raise Exception("Postal code info not found")


def get_path_of_create_database() -> str:
    """
    Function that retrieve path of file to create database.

    Args:
        None.

    Returns:
        str: path of file to create database.
    """

    actual_path = Path(__file__).resolve()
    project_path = actual_path.parent.parent.parent.parent
    db_path = project_path / 'db' / 'create_db_tables_statement.sql'
    return str(db_path)

def get_path_sqlite_db() -> str:
    """
    Function that retrieve path of sqlite database file.

    Args:
        None.

    Returns:
         str: path of sqlite database file.
    """

    actual_path = Path(__file__).resolve()
    project_path = actual_path.parent.parent.parent.parent
    db_path = project_path / 'db' / 'mercadona-scraper-results.db'

    return str(db_path)

def get_path_csv_from_db() -> str:
    """
    Function that retrieve path of csv file.

    Args:
        None.

    Returns:
         str: path of csv file.
    """

    actual_path = Path(__file__).resolve()
    project_path = actual_path.parent.parent.parent.parent
    csv_path = project_path / 'csv' / 'mercadona-scraper-results.csv'
    return str(csv_path)

def get_path_ewo_ingredients_data() -> str:
    """
    Function that retrieve path of ewo ingredients file.

    Args:
        None.

    Returns:
         str: path of ewo ingredients file.
    """

    actual_path = Path(__file__).resolve()
    project_path = actual_path.parent.parent.parent.parent
    ewo_ingredients_path = project_path / 'external_data' / 'EWO_ingredients_translated.xlsx'
    return str(ewo_ingredients_path)

def clear_database() -> None:
    """
    Function that clear/create database.

    Args:
        None.

    Returns:
          None.
    """
    db_path = get_path_sqlite_db()
    db_create_file = get_path_of_create_database()

    with open(db_create_file, 'r') as sql_file:
        sql_script = sql_file.read()

    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.executescript(sql_script)
    db.commit()
    db.close()

def insert_product_data_to_database(info_products: list) -> None:
    """
    Function that insert product scraped data to database.

    Args:
        info_products (list): list of product scraped data.

    Returns:
        None.
    """

    inserts = []
    inserts_photos = []

    product: ProductScrapedDTO
    for product in info_products:
        inserts.append({'product': product, 'insert':product.get_insert_str()})

    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        for insert in inserts:
            cur.execute(insert['insert'][0], insert['insert'][1])
            product: ProductScrapedDTO
            product = insert['product']
            photos_to_insert = product.get_insert_photos(cur.lastrowid)
            for photo_to_insert in photos_to_insert:
                inserts_photos.append(photo_to_insert)

        for insert_photo in inserts_photos:
            cur.execute(insert_photo)
        conn.commit()

    conn.close()

def match_nutritional_data_with_each_product(
    nutriments_indexed_by_mercadona_id: dict,
    product_items: list
) -> list:
    data_to_return = []
    for mercadona_id, nutriment_data in nutriments_indexed_by_mercadona_id.items():
        for idx, product in enumerate(product_items):
            if product['id_product'] == mercadona_id:
                item = product_items[idx]
                item['nutriments'] = nutriment_data

                product_nutriments_dto = ProductNutrimentsDTO(
                        item['id'],
                        item['id_product'],
                        item['category'],
                        item['subcategory'],
                        item['second_subcategory'],
                        item['product_name'],
                        item['ingredients'],
                        item['nutriments']
                    )

                if 'alcohol_grades' in item and item['alcohol_grades']:
                    product_nutriments_dto.set_alcohol_grades(item['alcohol_grades'])

                data_to_return.append(product_nutriments_dto)

    return data_to_return