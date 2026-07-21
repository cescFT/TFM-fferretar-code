from google import genai
from google.genai import types
from gemini_integration.model_getter import get_gemini_model
from interact_db.update_gemini_model import update_is_blocked_gemini_models, update_last_petition_gemini_model
import time
import json
import requests
from io import BytesIO
from PIL import Image

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
        "Vull que em retornis també l'origen del producte, en cas que ho tinguis clar en castellà."
        "A més, si trobes alguna certificació en l'aliment, vull que també m'ho retornis en anglès."
        "Finalment, també et passaré un llistat de possibles valors en format json i vull que em retornis també la millor coincidència amb el nom del producte."
        "* Nom del producte: @@product_name@@\n"
        "* Llistat possibles valors de ciqual: @@ciqual_possible_responses@@\n"
        "Si en les imatges no trobes cap informació nutricional, retorna únicament un JSON amb les dades que hagis pogut trobar de les que t'he demanat (origen, certificacions i ciqual_data).\n"
        "Si no trobes cap de les informacions, retornaràs un JSON buit: {}"
        "</petition>\n"
        "\n"
        "<json_structure_with_data>\n"
        "{\n"
        '  "origen": "str" o None,\n'
        '  "ciqual_data": {"id": "int", "text": "str"} o None,\n'
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
        '  "certifications": ["str"] o None"'
        "}\n"
        "Nota: Si no trobes algun valor concret a la imatge, posa'l a None.\n"
        "</json_structure_with_data>"
    )

    gemini_model = get_gemini_model()

    for product in products_data:

        images = []

        for photo in product['photo_urls']:
            img_content = requests.get(photo, timeout=10)
            imatge = Image.open(BytesIO(img_content.content))
            images.append(imatge)

        prompt = prompt.replace("@@product_name@@", product['ciqual_text_to_search'])
        prompt = prompt.replace("@@ciqual_possible_responses@@", json.dumps(product['ciqual_possible_responses']))

        try:
            print(f"Provant la petició amb el model de gemini: {gemini_model.get_model_name()}")
            resposta_gemini = gemini_connection.models.generate_content(
                model=gemini_model.get_model_name(),
                contents=[prompt, images],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            update_last_petition_gemini_model(gemini_model)
        except Exception as e:
            gemini_model.set_is_blocked(True)
            update_last_petition_gemini_model(gemini_model)
            update_is_blocked_gemini_models([gemini_model])
            raise e

        try:
            nutritional_data = json.loads(resposta_gemini.text)
        except Exception as e:
            nutritional_data = {}

        nutritional_data_responses[product['id']] = nutritional_data
        print(f"GEMINI - Informació nutricional per al producte {product['product_name']} ({product['id_product']}): {nutritional_data}")
        time.sleep(8)
        #break # comentar aquesta linia si volem que ho faci per tots...

    return nutritional_data_responses