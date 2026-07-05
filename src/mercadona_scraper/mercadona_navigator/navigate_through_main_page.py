from selenium import webdriver
from bs4 import BeautifulSoup
import constants.constants_variables as constants_variables

BASIC_URL = constants_variables.constants_variables_getter("BASIC_URL")

def navigate_through_main_page(navigator: webdriver.Chrome) -> dict:
    links_to_follow = {}
    html = navigator.page_source
    soup = BeautifulSoup(html, 'html.parser')
    banner = soup.select("div.banner")[0]
    if banner:
        link = banner.find('a')['href'][1:]
        link = BASIC_URL + link
        title = banner.find('h2').text
        links_to_follow[title] = link
        print(f"S'ha trobat un banner: {title} - {link}")

    carousels = soup.select("section.section-carousel")
    print(f"S'han trobat {len(carousels)} carrusels de productes.")
    for idx, carousel in enumerate(carousels):
        titol_el = carousel.select_one("h2, h3")
        title = titol_el.text.strip() if titol_el else "Sense títol"
        link = carousel.find('a')
        if link:
            links_to_follow[title] = BASIC_URL + (link['href'][1:])
            print(f"- S'ha trobat un carousel: {title} - {BASIC_URL + (link['href'][1:])}")

    return links_to_follow