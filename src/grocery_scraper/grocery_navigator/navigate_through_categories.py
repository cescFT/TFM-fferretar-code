"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from grocery_scraper.constants.constants_variables import constants_variables_getter
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from selenium import webdriver

import time

EXCLUDED_CATEGORIES = constants_variables_getter("EXCLUDED_CATEGORIES")
EXCLUDED_SUB_CATEGORIES = constants_variables_getter("EXCLUDED_SUB_CATEGORIES")


def obtain_valid_urls_to_follow(
    navigator: webdriver.Chrome
) -> list:
    """
    Function that returns valid urls of subcategories to be followed.
    Args:
        navigator (webdriver.Chrome): Selenium navigator.

    Returns:
        list: list of valid urls of subcategories to be followed.
    """

    urls_to_follow = []

    wait = WebDriverWait(navigator, 60)
    categories = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.category-menu__item"))
    )

    for i, category in enumerate(categories):
        if i != 0:
            category.click()

        category_name = category.text.split("\n")[0]

        if category_name in EXCLUDED_CATEGORIES:
            continue

        subcategories = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.subhead1-r.category-item"))
        )

        for j, subcategory in enumerate(subcategories):
            if j != 0:
                subcategory.click()

            subcategory_name = subcategory.text

            if subcategory_name in EXCLUDED_SUB_CATEGORIES:
                continue

            url = navigator.current_url.split("?")[0]
            print(f"Category {category_name} - Subcategory {subcategory_name}: {url}")
            urls_to_follow.append({'category': category_name, 'subcategory': subcategory_name, 'url':url})

    return urls_to_follow

def calculate_items_available_to_be_sold(navigator: webdriver.Chrome, url: str) -> int:
    """
    Function responsible to calculate items available to be sold.
    Args:
        navigator (webdriver.Chrome): Selenium navigator.
        url (str): url of the page to be analyzed.

    Returns:
        int: number of items available to be sold.
    """

    navigator.get(url)
    time.sleep(5)
    html = navigator.page_source
    soup = BeautifulSoup(html, 'html.parser')

    products_container = soup.find_all("div", {"class": "product-container"})

    total_items = 0
    for product_container in products_container:
        product_items = product_container.find_all("div", {"class": "product-cell-container"})
        for product_item in product_items:
            button = product_item.find(
                "button",
                string=lambda text: text and "Añadir al carro" in text
            )

            if button:
                total_items += 1
            else:
                product_name = product_item.find("h4").text
                print(f"Skipping product {product_name} because is not available to be sold.")

    return total_items
