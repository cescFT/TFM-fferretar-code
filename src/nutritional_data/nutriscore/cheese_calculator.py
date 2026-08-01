"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from nutriscore.general_food_calculator import calculate as calculate_general_food


def calculate(nutriments:dict) -> dict:
    """
    Calculate nutriscore for cheese product.

    Args:
        nutriments (dict): nutriments of cheese products.

    Returns:
        dict: nutriscore of cheese product.
    """

    return calculate_general_food(nutriments, False, True)
