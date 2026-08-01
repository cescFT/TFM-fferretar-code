"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from random_user_agent.params import OperatingSystem, SoftwareName
from random_user_agent.user_agent import UserAgent

def create_selenium_driver(test = False) -> webdriver.Chrome:
    """
    Function that creates a Chrome selenium driver.

    Args:
        test (bool). By default is false. Otherwise if true, opens a Chrome navigator
        that allows to check what driver is doing.

    Return:
         webdriver.Chrome: A selenium driver using Chrome.
    """

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')

    if test:
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')

    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value]

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()

    options.add_argument('user-agent=' + user_agent)

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
