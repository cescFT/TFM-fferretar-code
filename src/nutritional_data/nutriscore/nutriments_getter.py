"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from dto.product_nutritional_data import ProductNutrimentsDTO, NutrimentDataDTO

def get_nutriments(
        nutriments_to_get: list,
        product: ProductNutrimentsDTO
) -> dict:
    """
    Function that parses nutriments data from database to dict in order to calculate nutriscore.

    Args:
        nutriments_to_get (list): Nutriments data to parse.
        product (ProductNutrimentsDTO): Product to be parsed.

    Returns:
        dict: Nutriment data for calculate nutriscore.
    """


    to_return = {}
    nutriments_product = product.get_nutriments()

    for nutriment_name in nutriments_to_get:
        found = False
        nutriment: NutrimentDataDTO
        for nutriment in nutriments_product:
            if nutriment_name in nutriment.get_nutriment_name():
                if nutriment.get_nutriment_unit() == "kcal":
                    continue
                quantity = nutriment.get_nutriment_value()
                to_return[nutriment_name] = quantity

                if nutriment_name == "sal":
                    to_return["sodi"] = quantity / 2.5

                found = True
                break

        if not found:
            to_return[nutriment_name] = 0

    return to_return
