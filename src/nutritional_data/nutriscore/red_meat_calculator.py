from nutriscore.general_food_calculator import calculate as calculate_general_food


def calculate(nutriments:dict) -> dict:
    return calculate_general_food(nutriments, True)
