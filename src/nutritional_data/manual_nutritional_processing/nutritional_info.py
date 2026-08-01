"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from gemini_integration.request import PROMPT_GEMINI
import json

def get_manual_data_from_foods(products_data: list) -> dict:
    """
    Function that enables user to add product information manually.

    Args:
        products_data (list): list of products data.

    Returns:
        dict: Dictionary with manual data.
    """

    nutritional_data_responses = {}

    for product in products_data:
        print("Prompt:\n\n")
        prompt = PROMPT_GEMINI.replace("@@product_name@@", product['ciqual_text_to_search'])
        prompt = prompt.replace("@@ciqual_possible_responses@@", json.dumps(product['ciqual_possible_responses']))
        prompt += "\n Retorna el json en una sola línia"

        print(prompt)

        print("\n\nPhotos:")
        for photo in product['photo_urls']:
            print("* :" + photo)


        json_data = input(product['product_name'] + "("+str(product['id'])+"-"+str(product['id_product'])+")> ")
        data_processed = json.loads(json_data)
        if data_processed and "sal" in data_processed and data_processed['sal'] and not data_processed['sodi']:
            sal_data = data_processed['sal']
            sal_quantity = sal_data['quantity']
            data_processed['sodi'] = {"quantity": sal_quantity * 400, "units": "mg" }
        nutritional_data_responses[product['id']] = data_processed
        print("=============================================================\n")


    return nutritional_data_responses
