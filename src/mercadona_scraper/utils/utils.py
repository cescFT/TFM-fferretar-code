from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from constants.constants_variables import constants_variables_getter
import sqlite3
from pathlib import Path


def accept_cookies(driver: webdriver.Chrome) -> None:
    try:
        boto_cookies = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//button[contains(text(), 'Aceptar')] | //button[@data-testid='cookie-policy-accept']"))
        )
        boto_cookies.click()
        print("Cookies acceptades.")
    except Exception:
        print("No ha aparegut el cartell de cookies o s'ha tancat automàticament.")

def process_postal_code(driver:webdriver.Chrome, postal_code: str) -> None:

    print(f"Introduint el codi postal: {postal_code}...")
    input_cp = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "postalCode"))
    )
    input_cp.clear()
    input_cp.send_keys(postal_code)

    input_cp.send_keys(Keys.RETURN)

def get_postal_code_from_wh_id(wh_id: str) -> str:
    constants_name = [
        "BCN_DATA",
        "TGN_DATA",
        "VALLS_DATA"
    ]

    for constant in constants_name:
        city_data = constants_variables_getter(constant)
        if city_data['WH'] == wh_id:
            return city_data['POSTAL_CODE']

    raise Exception("Postal code info not found")


def get_path_sqlite_db() -> str:
    actual_path = Path(__file__).resolve()
    project_path = actual_path.parent.parent.parent.parent
    db_path = project_path / 'db' / 'mercadona-scraper-results.db'

    return str(db_path)

def get_path_csv_from_db() -> str:
    actual_path = Path(__file__).resolve()
    project_path = actual_path.parent.parent.parent.parent
    csv_path = project_path / 'csv' / 'mercadona-scraper-results.csv'
    return str(csv_path)

def insert_product_data_to_database(info_products: list) -> None:
    inserts = []
    inserts_photos = []
    for product in info_products:
        inserts.append({'product': product, 'insert':product.get_insert_str()})

    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        for insert in inserts:
            cur.execute(insert['insert'][0], insert['insert'][1])
            photos_to_insert = insert['product'].get_insert_photos(cur.lastrowid)
            for photo_to_insert in photos_to_insert:
                inserts_photos.append(photo_to_insert)

        for insert_photo in inserts_photos:
            cur.execute(insert_photo)
        conn.commit()

    conn.close()