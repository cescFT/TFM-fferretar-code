import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup

BASIC_URL = "https://tienda.mercadona.es/"


def inicialitzar_botiga_mercadona(codi_postal="43800", debug=True):

    if debug:
        options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.maximize_window()
    else:
        options = webdriver.ChromeOptions()

        # 1. ACTIVA EL MODE HEADLESS
        # Actualment, Google recomana fer servir '--headless=new' en comptes de '--headless' a seques.
        options.add_argument('--headless=new')

        # 2. FIXA LA MIDA DE LA FINESTRA (Molt important!)
        # Si no ho fas, el mode invisible a vegades obre una finestra minúscula de mòbil,
        # amagant el botó "Continuar" i fent petar el teu script.
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')  # Ajuda a evitar errors gràfics en l'execució en segon pla

        # 3. TRUC ANTIBLOQUEIG (Cloudflare)
        # Quan fas servir el mode headless, Chrome avisa a la web dient: "Hola, sóc un HeadlessChrome".
        # Les webs com Mercadona ho detecten i et bloquegen a l'instant.
        # Li canviem el "DNI" (User-Agent) perquè es pensi que som un usuari normal des de Windows:

        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value]

        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

        # Get Random User Agent String.
        user_agent = user_agent_rotator.get_random_user_agent()

        options.add_argument(
            'user-agent='+ user_agent)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1. Anar a la web de Mercadona
        print("Obrint Mercadona...")
        driver.get(BASIC_URL)

        # 2. Acceptar les Cookies (si apareix el banyador)
        try:
            boto_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[contains(text(), 'Aceptar')] | //button[@data-testid='cookie-policy-accept']"))
            )
            boto_cookies.click()
            print("Cookies acceptades.")
        except Exception:
            print("No ha aparegut el cartell de cookies o s'ha tancat automàticament.")

        # 3. Introduir el Codi Postal
        print(f"Introduint el codi postal: {codi_postal}...")
        input_cp = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "postalCode"))
        )
        input_cp.clear()
        input_cp.send_keys(codi_postal)

        # TRUC MÀGIC: Simulem que premem la tecla "ENTER" des del mateix camp de text
        input_cp.send_keys(Keys.RETURN)

        time.sleep(5)

        return driver

    except Exception as e:
        print(f"Alguna cosa ha fallat durant l'inici: {e}")
        driver.quit()
        return None


if __name__ == "__main__":
    navegador = inicialitzar_botiga_mercadona(codi_postal="43800", debug=False)

    links_to_follow = []

    if navegador:

        html_pàgina = navegador.page_source
        soup = BeautifulSoup(html_pàgina, 'html.parser')
        banner = soup.select("div.banner")[0]
        if banner:
            link = banner.find('a')['href'][1:]
            links_to_follow.append(BASIC_URL+link)

        carousels = soup.select("section.section-carousel")
        print(f"S'han trobat {len(carousels)} carrusels de productes.")
        for idx, carousel in enumerate(carousels):
            titol_el = carousel.select_one("h2, h3")
            titol = titol_el.text.strip() if titol_el else "Sense títol"
            print(f" - Carrusel {idx + 1}: {titol}")
            link = banner.find('a')
            if link:
                links_to_follow.append(BASIC_URL+(link['href'][1:]))


        navegador.quit()

    else:
        print("No s'ha pogut iniciar el navegador. Tancant sraper")

    print(links_to_follow)