from dto.product_nutritional_data import ProductNutrimentsDTO
from nutriscore.parse_mercadona_category_to_nutriscore_category import parse
from nutriscore.nutriments_getter import get_nutriments
from constants.constants_variables import constants_variables_getter
from nutriscore.general_food_calculator import calculate as calculate_general_food
from nutriscore.red_meat_calculator import calculate as calculate_red_meat
from nutriscore.cheese_calculator import calculate as calculate_cheese
from nutriscore.fats_oils_nuts_seeds_calculator import calculate as calculate_fats_oils_nuts_seeds
from nutriscore.beverages_calculator import calculate as calculate_beverages

NUTRIMENTS_NUTRISCORE = constants_variables_getter("NUTRIMENTS_NUTRISCORE")

def calculate_nutriscore(product: ProductNutrimentsDTO) -> dict:
    data_to_return = {}
    print(f"Producte: {product.get_product_name()}\n")
    category_nutriscore = parse(product)

    print(f"Categoria nutriscore: {category_nutriscore}\n")

    if not category_nutriscore:
        return data_to_return

    if category_nutriscore != "WATER":
        nutriments_to_get = NUTRIMENTS_NUTRISCORE[category_nutriscore]

        nutriments = get_nutriments(nutriments_to_get, product)

        print(product.get_ingredients())
        fruits = input("Indica el percentatge de fruita/llegums >")
        if not fruits:
            fruits = 0

        nutriments["fruit_percentage"] = float(fruits)

    if category_nutriscore == "GENERAL_FOOD":
        data_to_return = calculate_general_food(nutriments)
    elif category_nutriscore == "RED_MEAT":
        data_to_return = calculate_red_meat(nutriments)
    elif category_nutriscore == "CHEESE":
        data_to_return = calculate_cheese(nutriments)
    elif category_nutriscore == "FATS_OILS_NUTS_SEEDS":
        data_to_return = calculate_fats_oils_nuts_seeds(nutriments)
    elif category_nutriscore == "BEVERAGES":
        nutriments['ingredients'] = product.get_ingredients()
        data_to_return = calculate_beverages(nutriments)
    elif category_nutriscore == "WATER":
        data_to_return = {'letter': 'A'}

    data_to_return['request_made'] = nutriments
    data_to_return['nutriscore_category'] = category_nutriscore

    return data_to_return

