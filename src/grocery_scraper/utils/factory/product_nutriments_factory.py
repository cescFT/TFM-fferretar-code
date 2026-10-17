"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""
from dto.product_nutritional_data import ProductNutrimentsDTO
from interact_db.get_data_from_db import get_product_information_by_product_grocery_id
from grocery_scraper.constants.constants_variables import constants_variables_getter

BASIC_NUTRIMENTS_TO_GET = constants_variables_getter("BASIC_NUTRIMENTS_TO_GET")
NO_NUTRIMENT_DATA = BASIC_NUTRIMENTS_TO_GET[0]

def create_from_product_id(product_id: str) -> ProductNutrimentsDTO:
    """
    Function to generate product dto with only product grocery id.
    Args:
        product_id (str): product grocery id

    Returns:
        ProductNutrimentsDTO: product dto
    """

    product_data = get_product_information_by_product_grocery_id(product_id)

    product_info = product_data['product']
    nutriments = product_data['nutriments']

    nutriments_data = []
    for nutriment in nutriments:
        if nutriment[0] == int(NO_NUTRIMENT_DATA):
            continue

        nutriments_data.append({
            'id_nutriment': nutriment[0],
            'nutriment_name': nutriment[1],
            'quantity': nutriment[2],
            'units': nutriment[3]
        })

    product_dto = ProductNutrimentsDTO(
        id = product_info[0],
        id_product=product_info[1],
        category=product_info[2],
        subcategory=product_info[3],
        second_subcategory=product_info[4],
        product_name=product_info[5],
        ingredients=product_info[6],
        nutriments=nutriments_data
    )

    product_dto.set_alcohol_grades(product_info[7])

    return product_dto
