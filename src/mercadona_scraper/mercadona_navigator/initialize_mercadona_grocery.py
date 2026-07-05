import time
from selenium import webdriver
import constants.constants_variables as constants_variables

from driver_creator.creator import create_selenium_driver
import utils.utils as utils

BASIC_URL = constants_variables.constants_variables_getter("BASIC_URL")

def initialize(postal_code, test=False, url: str = "") -> webdriver.Chrome | None:

    driver = create_selenium_driver(test)

    try:
        print("Obrint Mercadona...")
        if not url:
            url = BASIC_URL

        driver.get(url)

        utils.accept_cookies(driver)
        utils.process_postal_code(driver, postal_code)

        time.sleep(5)

        return driver

    except Exception as e:
        print(f"Alguna cosa ha fallat durant l'inici: {e}")
        driver.quit()
        return None