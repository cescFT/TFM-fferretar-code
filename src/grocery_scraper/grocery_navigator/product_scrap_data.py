"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from interact_db.get_data_from_db import retrieve_product_data_from_grocery_id
from constants import constants_variables
from grocery_api import utils as grocery_api_caller
from dto.product_scrap_data_request import ProductScrapDataRequestDTO
from dto.product_scrap_data import ProductScrapedDTO
from utils.utils import get_postal_code_from_wh_id

import datetime
import re

NOT_INGREDIENTS_SAME_NAME_CATEGORIES = constants_variables.constants_variables_getter('NOT_INGREDIENTS_SAME_NAME_CATEGORIES')
EXCLUDED_CATEGORIES = constants_variables.constants_variables_getter('EXCLUDED_CATEGORIES')
EXCLUDED_SUB_CATEGORIES = constants_variables.constants_variables_getter('EXCLUDED_SUB_CATEGORIES')

def get_urls_and_data_from_specific_page(
    product: webelement.WebElement,
    navigator: webdriver.Chrome,
    position: int,
    title_text: str,
    main_page_position: int
) -> dict:
    """
    Function that retrieve all urls of products in specific page and returns basic information of each product.

    Args:
        product (webelement.WebElement): Product as web element to get basic data of the product.
        navigator (webdriver.Chrome): Chrome webdriver.
        position (int): Position of the product in the page.
        title_text (str): Title of the category.
        main_page_position (int): Position of the page in the main page.

    Returns:
        dict: Basic data of each product in the landing.
    """

    products_to_scrap_urls_result = {}
    try:
        product.click()
        url_product = navigator.current_url
        wait = WebDriverWait(navigator, 60)
        close_button_modal = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.modal-content__close"))
        )

        category = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.subhead1-r"))
        ).text

        category = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', category).strip()

        subcategory = WebDriverWait(navigator, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.subhead1-sb"))
        ).text
        subcategory = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', subcategory).strip()

        append_item = True
        if category in EXCLUDED_CATEGORIES:
            print(f"Discard product {url_product} because is of category {category}")
            append_item = False

        if append_item and subcategory in EXCLUDED_SUB_CATEGORIES:
            print(f"Discard product {url_product} because is from subcategory {subcategory}")
            append_item = False

        if append_item and url_product:
            products_to_scrap_urls_result = {
                'url': url_product,
                'category': category,
                'subcategory': subcategory,
                'title_in_page_product': title_text,
                'position': position,
                'main_page_position': main_page_position
            }

        close_button_modal.click()
    except TimeoutException:
        print(f"TimeoutException: The product took to long on loading. Skip to the next.")

        try:
            ActionChains(navigator).send_keys(Keys.ESCAPE).perform()
        except Exception as e:
            print(f"Modal cannot be closed with ESC button: {e}")

    return products_to_scrap_urls_result

def process_thread_product_scrap_data(item: ProductScrapDataRequestDTO) -> ProductScrapedDTO|None:
    """
    Function that executes a single thread. Each thread is a product.

    Args:
        item (ProductScrapDataRequestDTO): Request of product.


    Returns:
        ProductScrapedDTO|None: Information of product if all is correct.
    """

    try:
        return get_product_scrap_data(item.get_product_data_item(), item.get_title(), item.get_wh_code())
    except Exception as e:
        print(f"Error processing the product {e}")
        return None


def get_product_scrap_data(
        data:dict,
        title_category_main_page: str,
        wh_id: str
) -> ProductScrapedDTO:
    """
    Function that gets all information of product. It gets information of the requests and then use
    grocery online api in order to get product information.

    Args:
        data (dict): Basic information of the product.
        title_category_main_page (str): Title of the category in the main page.
        wh_id (str): Warehouse id.

    Returns:
        ProductScrapedDTO: Product information.
    """

    id = data['url'].split("/")[4]
    main_page_position = data['main_page_position']
    response_api = grocery_api_caller.get_data_from_api(id, wh_id)
    en_response_api = grocery_api_caller.get_data_from_api(id, wh_id, "en")

    product_name = response_api['display_name']
    en_product_name = en_response_api['display_name']
    categories = en_response_api['categories']
    origin = response_api['origin']
    if not origin:
        origin = ""

    category_en = categories[0]['name'] if categories else ""
    subcategory_en = ""
    if categories and categories[0] and "categories" in categories[0]:
        subcategory_en = categories[0]["categories"][0]["name"]

    second_subcategory = ""
    category_es = response_api['categories'][0]
    if category_es and "categories" in category_es:
        second_subcategory_data = category_es["categories"][0]
        if second_subcategory_data and "categories" in second_subcategory_data:
            second_subcategory_data = second_subcategory_data["categories"][0]
            second_subcategory = second_subcategory_data["name"]

    second_subcategory_en = ""
    category_data_en = en_response_api['categories'][0]
    if category_data_en and "categories" in category_data_en:
        second_subcategory_data = category_data_en["categories"][0]
        if second_subcategory_data and "categories" in second_subcategory_data:
            second_subcategory_data = second_subcategory_data["categories"][0]
            second_subcategory_en = second_subcategory_data["name"]

    alcohol_grades = ''
    if "details" in response_api:
        item_details = response_api['details']
        if "alcohol_by_volume" in item_details and item_details["alcohol_by_volume"]:
            alcohol_grades = item_details["alcohol_by_volume"]
            alcohol_grades = alcohol_grades.replace("º", "")

    bar_code = response_api['ean']
    ingredients = response_api['nutrition_information']['ingredients']
    if ingredients is None:
        ingredients = ""
    ingredients = re.sub(r"<.*?>", "", ingredients)

    if not ingredients and data['category'] in NOT_INGREDIENTS_SAME_NAME_CATEGORIES:
        ingredients = product_name

    ingredients = ingredients.lower()
    new_arrival = response_api['is_new_arrival']

    price_instructions = response_api['price_instructions']
    quantity = price_instructions['unit_size']
    units = price_instructions['size_format']
    price = price_instructions['bulk_price']
    units_price = "€/"+units
    pvp = price_instructions['unit_price']

    previous_pvp = price_instructions['previous_unit_price']
    if previous_pvp:
        previous_pvp = previous_pvp.strip()

    photos = response_api['photos']
    photo_data = []
    for photo in photos:
        photo_data.append(photo['regular'])

    now = datetime.datetime.now()
    year = now.strftime("%Y")
    year_iso, week_num, day = now.isocalendar()

    product_data_from_db = retrieve_product_data_from_grocery_id(id)

    has_found_nutriments = False
    if product_data_from_db:
        if not origin:
            origin = product_data_from_db['origin']

        has_found_nutriments = product_data_from_db['found_nutriments']

    dto = ProductScrapedDTO(
        date=now.strftime("%Y-%m-%d %H:%M:%S"),
        week_num=week_num,
        year=year,
        id_product=id,
        position=data['position'],
        category=data['category'],
        subcategory=data['subcategory'],
        en_category=category_en,
        en_subcategory=subcategory_en,
        title_category_main_page=title_category_main_page,
        title_in_page_product=data['title_in_page_product'],
        photos=photo_data,
        product_name=product_name,
        en_product_name=en_product_name,
        quantity=quantity,
        quantity_units=units,
        price=price,
        price_units=units_price,
        pvp=pvp,
        ingredients=ingredients,
        bar_code=bar_code,
        is_new_arrival=new_arrival,
        previous_pvp=previous_pvp,
        postal_code=get_postal_code_from_wh_id(wh_id),
        origin=origin,
        second_subcategory=second_subcategory,
        alcohol_grades=alcohol_grades,
        second_subcategory_en=second_subcategory_en,
        has_found_nutriments=has_found_nutriments,
        main_page_position=main_page_position,
    )

    if product_data_from_db:
        if product_data_from_db['nutriscore']:
            dto.set_nutriscore(product_data_from_db['nutriscore'])

        if product_data_from_db['planetscore']:
            dto.set_planetscore(product_data_from_db['planetscore'])

        if product_data_from_db['ciqual_text']:
            dto.set_ciqual_text(product_data_from_db['ciqual_text'])

        if product_data_from_db['ciqual_id']:
            dto.set_ciqual_id(product_data_from_db['ciqual_id'])

        if product_data_from_db['ewo_ultra_processed_punctuation']:
            dto.set_ewo_ultra_processed_punctuation(product_data_from_db['ewo_ultra_processed_punctuation'])

    return dto
