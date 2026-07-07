from google import genai
from google.genai import types
import json
import requests
from io import BytesIO
from PIL import Image
from constants.constants_variables import constants_variables_getter

EXCLUDE_CATEGORY_TO_GET_NUTRIMENTS = constants_variables_getter('EXCLUDE_CATEGORY_TO_GET_NUTRIMENTS')

def request_gemini(gemini_connection: genai.Client, products_data: list) -> dict:
    nutritional_data_responses = {}

    prompt = (
        "<context>\n"
        "Ets un expert nutricionista especialitzat a analitzar etiquetes de productes de supermercat i extreure'n el valor nutricional. "
        "La teva tasca és analitzar les imatges d'aquest producte. "
        "Troba la taula nutricional (o la zona de text on parli de valors nutricionals) "
        "i extreu els valors exactes per cada 100 g o 100 ml (en cas de beguda).\n"
        "Si et trobes les dades escrites en molts idiomes, centra't només en el castellà o el català.\n"
        "</context>\n"
        "\n"
        "<petition>\n"
        "Retorna els resultats ESTRICTAMENT en un format JSON vàlid. No afegeixis text abans ni després, ni facis servir blocs de codi Markdown (```json). "
        "En aquest JSON vull que calculis i incloguis la lletra del Nutri-Score (A, B, C, D o E) basant-te en l'últim algoritme vigent. "
        "Si en les imatges no trobes cap informació nutricional, retorna únicament un JSON buit: {}\n"
        "</petition>\n"
        "\n"
        "<json_structure_with_data>\n"
        "{\n"
        '  "nutriscore": "str (A, B, C, D, E) o None",\n'
        '  "energia_kcal": "float o None",\n'
        '  "energia_kj": "float o None",\n'
        '  "greixos_totals": {"quantity": "float", "units": "str"} o None,\n'
        '  "greixos_saturats": {"quantity": "float", "units": "str"} o None,\n'
        '  "greixos_monoinsaturats": {"quantity": "float", "units": "str"} o None,\n'
        '  "greixos_poliinsaturats": {"quantity": "float", "units": "str"} o None,\n'
        '  "hidrats_carboni": {"quantity": "float", "units": "str"} o None,\n'
        '  "sucres": {"quantity": "float", "units": "str"} o None,\n'
        '  "fibra": {"quantity": "float", "units": "str"} o None,\n'
        '  "proteines": {"quantity": "float", "units": "str"} o None,\n'
        '  "sal": {"quantity": "float", "units": "str"} o None,\n'
        '  "sodi": {"quantity": "float", "units": "str"} o None,\n'
        '  "vitamina_a": {"quantity": "float", "units": "str"} o None,\n'
        '  "vitamina_c": {"quantity": "float", "units": "str"} o None,\n'
        '  "calci": {"quantity": "float", "units": "str"} o None,\n'
        '  "ferro": {"quantity": "float", "units": "str"} o None\n'
        '  "fosfor": {"quantity": "float", "units": "str"} o None\n'
        '  "magnesi": {"quantity": "float", "units": "str"} o None\n'
        '  "potasi": {"quantity": "float", "units": "str"} o None\n'
        '  "vitamina_d": {"quantity": "float", "units": "str"} o None\n'
        '  "vitamina_e": {"quantity": "float", "units": "str"} o None\n'
        '  "vitamina_b6": {"quantity": "float", "units": "str"} o None\n'
        '  "vitamina_b12": {"quantity": "float", "units": "str"} o None\n'
        '  "acid_folic": {"quantity": "float", "units": "str"} o None\n'
        '  "zinc": {"quantity": "float", "units": "str"} o None\n'
        "}\n"
        "Nota: Si no trobes algun valor concret a la imatge, posa'l a None.\n"
        "</json_structure_with_data>"
    )

    for product in products_data:
        images = []

        if product['category'] in EXCLUDE_CATEGORY_TO_GET_NUTRIMENTS:
            nutritional_data_responses[product['id']] = {}
            continue

        for photo in product['photo_urls']:
            img_content = requests.get(photo, timeout=10)
            imatge = Image.open(BytesIO(img_content.content))
            images.append(imatge)


        resposta_gemini = gemini_connection.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, images],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        try:
            nutritional_data = json.loads(resposta_gemini.text)
        except Exception as e:
            nutritional_data = {}

        nutritional_data_responses[product['id']] = nutritional_data
        print(f"GEMINI - Informació nutricional per al producte {product['product_name']} ({product['id_product']}): {nutritional_data}")
        #break # comentar aquesta linia si volem que ho faci per tots...

    return nutritional_data_responses