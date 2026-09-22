"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from nutriscore.general_food_calculator import calculate as calculate_general_food


def calculate(nutriments:dict) -> dict:
    """
   Calculate nutriscore for red meat product.

   Args:
       nutriments (dict): nutriments of red meat products.

   Returns:
       dict: nutriscore of red meat product.
   """

    return calculate_general_food(nutriments, True)
