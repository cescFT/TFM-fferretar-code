from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from constants import constants_variables
from mercadona_api import utils as mercadona_api_caller
import datetime
import re
from dto.product_scrap_data import ProductScrapData

NOT_INGREDIENTS_SAME_NAME_CATEGORIES = constants_variables.constants_variables_getter('NOT_INGREDIENTS_SAME_NAME_CATEGORIES')
EXCLUDED_CATEGORIES = constants_variables.constants_variables_getter('EXCLUDED_CATEGORIES')
EXCLUDED_SUB_CATEGORIES = constants_variables.constants_variables_getter('EXCLUDED_SUB_CATEGORIES')

def get_urls_and_data_from_specific_page(
    product: webelement.WebElement,
    navigator: webdriver.Chrome,
    position: int,
    title_text: str
) -> dict:
    products_to_scrap_urls_result = {}
    product.click()
    url_product = navigator.current_url
    close_button_modal = WebDriverWait(navigator, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button.modal-content__close"))
    )

    category = WebDriverWait(navigator, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.subhead1-r"))
    ).text

    category = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', category).strip()

    subcategory = WebDriverWait(navigator, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.subhead1-sb"))
    ).text
    subcategory = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', subcategory).strip()

    append_item = True
    if category in EXCLUDED_CATEGORIES:
        print(f"Descartem producte {url_product} per ser de la categoria {category}")
        append_item = False

    if append_item and subcategory in EXCLUDED_SUB_CATEGORIES:
        print(f"Descartem producte {url_product} per ser de la subcategoria {subcategory}")
        append_item = False

    if append_item and url_product:
        products_to_scrap_urls_result = {
            'url': url_product,
            'category': category,
            'subcategory': subcategory,
            'title_in_page_product': title_text,
            'position': position,
        }

    close_button_modal.click()

    return products_to_scrap_urls_result

def process_thread_product_scrap_data(item: ProductScrapData):
    try:
        return get_product_scrap_data(item.get_product_data_item(), item.get_title(), item.get_wh_code())
    except Exception as e:
        print(f"Error processant el producte {e}")
        return None


def get_product_scrap_data(
        data:dict,
        title_category_main_page: str,
        wh_id: str
) -> dict:
    id = data['url'].split("/")[4]
    response_api = mercadona_api_caller.get_data_from_api(id, wh_id)

    product_name = response_api['display_name']
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

    result = {
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'id_product': id,
        'position': data['position'],
        'category': data['category'],
        'subcategory': data['subcategory'],
        'title_category_main_page': title_category_main_page,
        'title_in_page_product': data['title_in_page_product'],
        'photos': response_api['photos'],
        'product_name': product_name,
        'quantity': quantity,
        'quantity_units': units,
        'price': price,
        'price_units': units_price,
        'pvp': pvp,
        'ingredients': ingredients,
        'bar_code': bar_code,
        'is_new_arrival': new_arrival,
        'previous_pvp': previous_pvp
    }

    return result