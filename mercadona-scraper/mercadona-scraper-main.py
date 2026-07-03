from mercadona_navigator import product_scrap_data
from mercadona_navigator.initialize_mercadona_grocery import initialize
import argparse
import time
from constants.constants_variables import constants_variables_getter
from mercadona_navigator.navigate_through_main_page import navigate_through_main_page

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
    start_date_total = time.perf_counter()
    for title, url in urls_to_follow.items():
        start_date = time.perf_counter()
        navigator = initialize(postal_code)
        products_to_scrap_urls[title] = []

        navigator.get(url)
        print(f"Agafant les urls dels productes de {title} - {url}")

        element_h2 = WebDriverWait(navigator, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2.section__header.headline1-b"))
        )

        title_text = element_h2.text
        print(f"El títol extret és: {title_text}")

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

        navigator.quit()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_date
        print(f"Total productes de {title}: {len(products_to_scrap_urls[title])}. Temps execució {elapsed_time:.2f} segons.")
        break

    end_time_total = time.perf_counter()
    print(f"Temps total per totes les categories principals: {((end_time_total - start_date_total)/60):.2f} min.")


    ###### TODO: IMPLEMENTAR TRHEADS AQUI! COMPROVAR QUE TOT S'AGAFI OK EN TOTS ELS PRODUCTES
    info_products = []
    for title, product_data in products_to_scrap_urls.items():
        for product_data_item in product_data:
            product_info = product_scrap_data.get_product_scrap_data(product_data_item, title)
            info_products.append(product_info)
            print(f"Producte {product_info['product_name']} de {title} processat correctament")
        print(info_products)
    #####

    # desar a sqlite?
    # pensar tema de les dades valors nutricionals + nutriscore preguntar a gemini <--- TODO despres de fer threads i recuperar tots els productes correctament
    # a traves de les imatges que se li passaran a un prompt...
    # generar api key i posar-la a un .env...

if __name__ == "__main__":
    execute_scraper()