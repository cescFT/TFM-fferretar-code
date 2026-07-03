from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver


def accept_cookies(driver: webdriver.Chrome) -> None:
    try:
        boto_cookies = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//button[contains(text(), 'Aceptar')] | //button[@data-testid='cookie-policy-accept']"))
        )
        boto_cookies.click()
        print("Cookies acceptades.")
    except Exception:
        print("No ha aparegut el cartell de cookies o s'ha tancat automàticament.")

def process_postal_code(driver:webdriver.Chrome, postal_code: str) -> None:

    print(f"Introduint el codi postal: {postal_code}...")
    input_cp = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "postalCode"))
    )
    input_cp.clear()
    input_cp.send_keys(postal_code)

    input_cp.send_keys(Keys.RETURN)