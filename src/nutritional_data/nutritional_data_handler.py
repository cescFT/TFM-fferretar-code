from gemini_integration import connect
from google.genai import types
import json
import requests
from io import BytesIO
from PIL import Image

from interact_db import get_data_from_db
from interact_db.get_data_from_db import get_products_without_nutritional_data
from interact_db.update_products_to_db import update_food_found_nutriments
from constants.constants_variables import constants_variables_getter
from dto.product_nutritional_data import ProductNutritionalDataDTO, NutrientDTO

LIMIT_PRODUCTS = constants_variables_getter('LIMIT_PRODUCTS_TO_GET_NUTRITIONAL_DATA')
BASIC_NUTRIENTS_TO_GET = constants_variables_getter('BASIC_NUTRIENTS_TO_GET')
NO_DATA = BASIC_NUTRIENTS_TO_GET[0]
ENERGY_KCAL = BASIC_NUTRIENTS_TO_GET[1]
ENERGY_KJ = BASIC_NUTRIENTS_TO_GET[2]

if __name__ == '__main__':
    print("Inici script...")

    products_data = get_products_without_nutritional_data(int(LIMIT_PRODUCTS))

    gemini_connection = connect.create_connection_to_gemini()

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

    nutritional_data_responses = {}

    for product in products_data:
        images = []

        for photo in product['photo_urls']:
            img_content = requests.get(photo, timeout=10)
            imatge = Image.open(BytesIO(img_content.content))
            images.append(imatge)

        try:
            resposta_gemini = gemini_connection.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, images],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
        except Exception as e:
            print(f"Error: {e}")
            continue

        try:
            nutritional_data = json.loads(resposta_gemini.text)
        except Exception as e:
            nutritional_data = {}


        nutritional_data_responses[product['id']] = nutritional_data
        print(nutritional_data)
        #break # comentar aquesta linia si volem que ho faci per tots...


    nutriments = get_data_from_db.get_types_of_nutriments(BASIC_NUTRIENTS_TO_GET)
    nutriments_to_save = []
    for product in products_data:
        product_id = product['id']
        nutritional_data = nutritional_data_responses[product_id]

        if not nutritional_data:
            continue

        product_nutritional_data_dto = ProductNutritionalDataDTO(
            product_id,
            product['id_product'],
            product['category'],
            product['subcategory'],
            product['product_name'],
            product['photo_urls']
        )

        if not nutritional_data:
            no_data_nutriment = NutrientDTO('', 0, '')
            no_data_nutriment.set_nutrient_id(NO_DATA)
            product_nutritional_data_dto.nutrients.append(no_data_nutriment)
            print(
                f"No hi ha dades nutricionals per a {product_nutritional_data_dto.get_product_name()} "
                f"({product_nutritional_data_dto.get_mercadona_id()}) en la categoria {product_nutritional_data_dto.get_category()}"
            )
            nutriments_to_save.append(product_nutritional_data_dto)
            continue

        for key, value in nutritional_data.items():
            nutriment_data = NutrientDTO('', 0, '')
            if key == "nutriscore" and value:
                product_nutritional_data_dto.set_nutriscore(value)
                nutriment_data = None
            if key == "energia_kcal" and value:
                nutriment_data.set_nutrient_id(ENERGY_KCAL)
                nutriment_data.set_nutrient_value(value)
            if key == "energia_kj" and value:
                nutriment_data.set_nutrient_id(ENERGY_KJ)
                nutriment_data.set_nutrient_value(value)

            if not value:
                continue

            if type(value) == dict:
                name_nutriment = key + "_" + value['units']
                if name_nutriment in nutriments:
                    nutriment_id = nutriments[name_nutriment]
                    nutriment_data.set_nutrient_id(nutriment_id)
                    nutriment_data.set_nutrient_value(value['quantity'])
                else:
                    nutriment_data = NutrientDTO(name_nutriment, value['quantity'], value['units'])

            if nutriment_data:
                product_nutritional_data_dto.add_nutrient(nutriment_data)

        nutriments_to_save.append(product_nutritional_data_dto)

    update_food_found_nutriments(nutriments_to_save)
    print("Fi script.")

