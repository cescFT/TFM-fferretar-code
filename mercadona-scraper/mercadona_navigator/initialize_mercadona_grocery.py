import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import constants.constants_variables as constants_variables

from driver_creator.creator import create_selenium_driver

BASIC_URL = constants_variables.constants_variables_getter("BASIC_URL")

def initialize(postal_code, test=False) -> webdriver.Chrome | None:

    driver = create_selenium_driver(test)

    try:
        print("Obrint Mercadona...")
        driver.get(BASIC_URL)

        try:
            boto_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[contains(text(), 'Aceptar')] | //button[@data-testid='cookie-policy-accept']"))
            )
            boto_cookies.click()
            print("Cookies acceptades.")
        except Exception:
            print("No ha aparegut el cartell de cookies o s'ha tancat automàticament.")

        print(f"Introduint el codi postal: {postal_code}...")
        input_cp = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "postalCode"))
        )
        input_cp.clear()
        input_cp.send_keys(postal_code)

        input_cp.send_keys(Keys.RETURN)

        time.sleep(5)

        return driver

    except Exception as e:
        print(f"Alguna cosa ha fallat durant l'inici: {e}")
        driver.quit()
        return None