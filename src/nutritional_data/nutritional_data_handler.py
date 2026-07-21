from gemini_integration import connect
from gemini_integration.request import request_gemini

from interact_db import get_data_from_db
from interact_db.get_data_from_db import get_products_without_nutritional_data
from interact_db.update_products_to_db import update_food_found_nutriments
from constants.constants_variables import constants_variables_getter
from nutriments_processing.process_response import process_response_from_gemini

LIMIT_PRODUCTS = constants_variables_getter('LIMIT_PRODUCTS_TO_GET_NUTRITIONAL_DATA')
BASIC_NUTRIENTS_TO_GET = constants_variables_getter('BASIC_NUTRIENTS_TO_GET')
CERTIFICATIONS_BASIC = constants_variables_getter('CERTIFICATIONS_BASIC')
NO_CERTIFICATIONS = CERTIFICATIONS_BASIC[0]
NO_DATA = BASIC_NUTRIENTS_TO_GET[0]
ENERGY_KCAL = BASIC_NUTRIENTS_TO_GET[1]
ENERGY_KJ = BASIC_NUTRIENTS_TO_GET[2]

def nutritional_data_handler() -> None:
    products_data = get_products_without_nutritional_data(int(LIMIT_PRODUCTS))
    print(f"S'han trobat {len(products_data)} productes sense dades nutricionals.")
    print("Establint connexió amb gemini...")
    gemini_connection = connect.create_connection_to_gemini()
    print("Connexió establerta amb gemini.")
    print("S'estan enviant les peticions a gemini...")
    nutritional_data_responses = request_gemini(gemini_connection, products_data)

    nutriments = get_data_from_db.get_types_of_nutriments(BASIC_NUTRIENTS_TO_GET)
    certifications = get_data_from_db.get_types_of_certifications(CERTIFICATIONS_BASIC)

    print("Processant respostes de gemini...")
    nutriments_to_save = process_response_from_gemini(
        products_data,
        nutritional_data_responses,
        NO_DATA,
        ENERGY_KCAL,
        ENERGY_KJ,
        nutriments,
        NO_CERTIFICATIONS,
        certifications
    )


    print("Desant les dades de la informació nutricional a base de dades...")
    update_food_found_nutriments(nutriments_to_save)
    print("Dades desades de la informació nutricional correctament a la base de dades.")


if __name__ == '__main__':
    print("Inici script...")
    nutritional_data_handler()
    print("Fi script.")

