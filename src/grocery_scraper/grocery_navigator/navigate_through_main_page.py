"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from selenium import webdriver
from bs4 import BeautifulSoup

import constants.constants_variables as constants_variables

BASIC_URL = constants_variables.constants_variables_getter("BASIC_URL")

def navigate_through_main_page(navigator: webdriver.Chrome) -> dict:
    """
    Function that navigates through main page and with BeautifulSoup gets urls to follow in next steps for
    get product information.

    Args:
        navigator (webdriver.Chrome): Chrome webdriver instance.

    Returns:
        dict: Dictionary with urls to follow in next steps.
    """

    links_to_follow = {}
    html = navigator.page_source
    soup = BeautifulSoup(html, 'html.parser')
    banner = soup.select("div.banner")[0]
    if banner:
        link = banner.find('a')['href'][1:]
        link = BASIC_URL + link
        title = banner.find('h2').text
        links_to_follow[title] = link
        print(f"A banner is found: {title} - {link}")

    carousels = soup.select("section.section-carousel")
    print(f"There are {len(carousels)} carrusels of products.")
    for idx, carousel in enumerate(carousels):
        titol_el = carousel.select_one("h2, h3")
        title = titol_el.text.strip() if titol_el else "Sense títol"
        link = carousel.find('a')
        if link:
            links_to_follow[title] = BASIC_URL + (link['href'][1:])
            print(f"- There is a carrusel: {title} - {BASIC_URL + (link['href'][1:])}")

    return links_to_follow
