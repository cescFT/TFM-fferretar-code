from mercadona_navigator.initialize_mercadona_grocery import initialize
import argparse
import re
from constants.constants_variables import constants_variables_getter
from mercadona_navigator.navigate_through_main_page import navigate_through_main_page

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EXCLUDED_CATEGORIES = constants_variables_getter('EXCLUDED_CATEGORIES')
EXCLUDED_SUB_CATEGORIES = constants_variables_getter('EXCLUDED_SUB_CATEGORIES')

def execute_scraper() -> None:
    parser = argparse.ArgumentParser(
        description="Mercadona Scraper"
    )

    parser.add_argument(
        "-cp",
        type=str,
        help="Postal Code variable name"
    )

    args = parser.parse_args()

    if args.cp:
        postal_code = constants_variables_getter[args.cp]
    else:
        postal_code = constants_variables_getter('POSTAL_CODE_VALLS')


    navigator = initialize(postal_code)

    if not navigator:
        raise Exception("No s'ha pogut inicialitzar el navegador. Tancant sraper")

    urls_to_follow = navigate_through_main_page(navigator)
    navigator.quit()

    products_to_scrap_urls = {}
    for title, url in urls_to_follow.items():
        navigator = initialize(postal_code, True)
        products_to_scrap_urls[title] = []

        navigator.get(url)
        print(f"Agafant les urls dels productes de {title} - {url}")

        element_h2 = WebDriverWait(navigator, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2.section__header.headline1-b"))
        )

        text_titol = element_h2.text
        print(f"El títol extret és: {text_titol}")

        products = WebDriverWait(navigator, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-cell-container"))
        )

        for product in products:
            product.click()
            url_product = navigator.current_url
            close_button_modal = WebDriverWait(navigator, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.modal-content__close"))
            )

            category = WebDriverWait(navigator, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.subhead1-r"))
            ).text

            category = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', category).strip()

            subcategory = WebDriverWait(navigator, 5).until(
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
                products_to_scrap_urls[title].append({
                    'url': url_product,
                    'category': category,
                    'subcategory': subcategory
                })

            close_button_modal.click()

        print(f"Total productes de {title}: {len(products_to_scrap_urls[title])}")
        navigator.quit()



if __name__ == "__main__":
    execute_scraper()