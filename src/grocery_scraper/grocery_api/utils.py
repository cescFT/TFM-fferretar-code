"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

import requests
import json

from constants.constants_variables import constants_variables_getter

MERCADONA_BASE_URL_API = constants_variables_getter('MERCADONA_BASE_URL_API')

def get_data_from_api(product_id: str, wh_id: str, lang:str = "es") -> dict:
    """
    Function in charge to create cURL petition to mercadona API and returns its response if it is correct.

    Args:
        product_id (str): Product ID.
        wh_id (str): Warehouse ID.
        lang (str): Language. Defaults to "es".

    Returns:
         dict: JSON response from Mercadona API if request is successful.

    Raise:
        Exception: If request fails.
    """

    url = MERCADONA_BASE_URL_API.replace("@@product_id@@", product_id)
    url = url.replace("@@wh@@", wh_id)
    url = url.replace("@@lang@@", lang)

    response = requests.get(url)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Error al obtener los datos de la API: {response.status_code}")
