from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

def create_selenium_driver(test = False) -> webdriver.Chrome:
    """
    Function that creates a selenium driver.

    Args:
        None.

    Return:
         webdriver.Chrome: A selenium driver using Chrome.
    """

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')

    if test:
        options = webdriver.ChromeOptions()

    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value]

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()

    options.add_argument(
        'user-agent=' + user_agent)

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)