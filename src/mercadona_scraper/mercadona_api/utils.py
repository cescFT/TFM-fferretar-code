from constants.constants_variables import constants_variables_getter
import requests
import json

MERCADONA_BASE_URL_API = constants_variables_getter('MERCADONA_BASE_URL_API')

def get_data_from_api(product_id: str, wh_id: str, lang:str = "es") -> dict:

    url = MERCADONA_BASE_URL_API.replace("@@product_id@@", product_id)
    url = url.replace("@@wh@@", wh_id)
    url = url.replace("@@lang@@", lang)

    response = requests.get(url)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Error al obtener los datos de la API: {response.status_code}")