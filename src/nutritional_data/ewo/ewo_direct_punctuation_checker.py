"""
TFM: The healthiness and sustainability of food promotions in a Spanish online supermarket

Author: Francesc Ferré Tarrés
"""

from dto.product_nutritional_data import ProductNutrimentsDTO
from grocery_scraper.constants.constants_variables import constants_variables_getter

SUBCATEGORIES_TO_HAVE_GOOD_EWO_WHEN_NO_INGREDIENTS = constants_variables_getter("SUBCATEGORIES_TO_HAVE_GOOD_EWO_WHEN_NO_INGREDIENTS")
SECOND_SUBCATEGORIES_TO_HAVE_GOOD_EWO_WHEN_NO_INGREDIENTS = constants_variables_getter("SECOND_SUBCATEGORIES_TO_HAVE_GOOD_EWO_WHEN_NO_INGREDIENTS")

def check_direct_punctuation(product: ProductNutrimentsDTO) -> bool:
    """
    Function to check if the product has direct a good punctuation.

    Args:
        product (ProductNutrimentsDTO): The product to check.

    Returns:
        bool: True if the product has direct a good punctuation, False otherwise.
    """

    if product.get_subcategory() in SUBCATEGORIES_TO_HAVE_GOOD_EWO_WHEN_NO_INGREDIENTS:
        return True

    if product.get_second_subcategory() in SECOND_SUBCATEGORIES_TO_HAVE_GOOD_EWO_WHEN_NO_INGREDIENTS:
        return True

    return False
