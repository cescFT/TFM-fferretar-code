"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

import time

from selenium import webdriver

import constants.constants_variables as constants_variables
from driver_creator.creator import create_selenium_driver
import utils.utils as utils

BASIC_URL = constants_variables.constants_variables_getter("BASIC_URL")

def initialize(postal_code: str, test: bool=False, url: str = "") -> webdriver.Chrome | None:
    """
    Function that initializes the chrome selenium webdriver.

    Args:
        postal_code (str): postal code.
        test (bool): If true generates a Chrome window and you can see how affect's code in live. Defaults to False.
        url (str): Url to follow.

    Returns:
         webdriver.Chrome | None: Selenium webdriver if all is correct. Otherwise, returns None.
    """

    driver = create_selenium_driver(test)

    try:
        print("Opening Online Grocery Supermarket...")
        if not url:
            url = BASIC_URL

        driver.get(url)

        utils.accept_cookies(driver)
        utils.process_postal_code(driver, postal_code)

        time.sleep(5)

        return driver

    except Exception as e:
        print(f"Something fails during starting session: {e}")
        driver.quit()
        return None
