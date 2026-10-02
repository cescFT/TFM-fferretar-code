"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from dto.ewo_reference import EwoReference
from ewo.extra_sugar_reverse_calculation_ai import reverse_calculation_extra_sugar
from dto.product_nutritional_data import ProductNutrimentsDTO, NutrimentDataDTO
from nutritional_data.ewo.parse_grocery_categories_to_ewo_categories import parse
from grocery_scraper.constants.constants_variables import constants_variables_getter
from ewo.ewo_matcher_ingredients import match_ewo_ingredients
from ewo.ewo_matcher_ingredients_rudimentary import match_ewo_ingredients as match_ewo_ingredients_rudimentary
from grocery_scraper.utils.utils import normalize_text
import pandas as pd

NUTRIMENTS_DM_EWO = constants_variables_getter("NUTRIMENTS_DM_EWO")

def calculate_ultraprocessed_punctuation(
    product: ProductNutrimentsDTO,
    ewo_ingredients: pd.DataFrame
) -> dict:
    """
    Function that calculates ultraprocessed punctuation.
    Args:
        product (ProductNutrimentsDTO): Product to calculate ultraprocessed punctuation.
        ewo_ingredients (pd.DataFrame): DataFrame with ewo ingredients.

    Returns:
        dict: Dictionary with ultraprocessed punctuation.
    """

    print("Calculating ultraprocessed punctuation for product: ",
          product.get_grocery_id(), " ", product.get_product_name()
          )

    category = parse(product)

    print("Category calculated: ", category)

    if not product.get_ingredients() or not category:
        print(f"The product {product.get_grocery_id()} {product.get_product_name()} has directly a good punctuation.")
        return {'qualification': "1"}

    punctuation_step1, ingredients_matched = calculate_first_step_punctuation(
        product.get_ingredients(),
        product.get_certifications(),
        ewo_ingredients
    )

    if punctuation_step1 != 4:
        punctuation_step2, extra_sugar_added = calculate_second_step_punctuation(product, category, ingredients_matched)

        qualification = calculate_third_step_punctuation(punctuation_step1, punctuation_step2)
    else:
        print("Punctuation of step 1 is 4, skipping step 2 because according with Ewö algorithm,"
              " the product is already ultraprocessed (4).")
        qualification = 4
        punctuation_step2 = None
        extra_sugar_added = None

    ingredients_matched_data = [
        {
            "name":ingredient.__dict__["ingredient_name"],
            "reference":ingredient.__dict__["reference"],
            "score":ingredient.__dict__["score"],
            "sugar":ingredient.__dict__["sugar"]
        } for ingredient in ingredients_matched
    ]

    punct_dict = {
        'step1': str(punctuation_step1),
        'step2': str(punctuation_step2),
        'qualification': str(qualification),
        'category': category,
        'ingredients_matched': ingredients_matched_data,
        'extra_sugar_added': extra_sugar_added
    }

    return punct_dict

def calculate_third_step_punctuation(step1_punct:int, step2_punct:int) -> int:
    """
    Function that calculates third step of ewo ultraprocessing punctuation
    Args:
        step1_punct (int): First step of ewo ultraprocessing punctuation.
        step2_punct (int): Second step of ewo ultraprocessing punctuation.

    Returns:
        int: Third step and global score of ewo ultraprocessing punctuation.
    """

    if step1_punct == 1:
        if step2_punct == 4:
            return 3
        return step2_punct

    if step1_punct == 2:
        if step2_punct <= 2:
            return 2

        return step2_punct

    if step1_punct == 3:
        if step2_punct <= 3:
            return 3
        return step2_punct

    return 4


def calculate_second_step_punctuation(
    product: ProductNutrimentsDTO,
    category: str,
    ingredients_matched: list
) -> tuple:
    """
    Function that calculates second step of ultraprocessing punctuation.
    Args:
        product (ProductNutrimentsDTO): Product to calculate ultraprocessed punctuation.
        category (str): Category of the product.
        ingredients_matched (list): List of ingredients matched.

    Returns:
        tuple: Second step of ultraprocessing punctuation and extra sugars added.
    """
    nutriments = product.get_nutriments()

    sugars_total = 0
    carbohydrate_total = 0
    nutriment: NutrimentDataDTO
    for nutriment in nutriments:
        if nutriment.get_nutriment_name() == "sucres_g":
            sugars_total = nutriment.get_nutriment_value()

        if nutriment.get_nutriment_name() == "hidrats_carboni_g":
            carbohydrate_total = nutriment.get_nutriment_value()

    ingredients_extra_sugar = []
    ingredient: EwoReference
    for ingredient in ingredients_matched:
        if ingredient.get_sugar():
            ingredients_extra_sugar.append(ingredient)

    extra_sugar = 0
    if len(ingredients_extra_sugar) > 0:
        print(f"Total sugars in {product.get_product_name()}: {sugars_total}g of {carbohydrate_total}g carbohydrates.")
        ingredient_names = ", ".join([ingredient.get_ingredient_name() for ingredient in ingredients_extra_sugar])
        extra_sugar = reverse_calculation_extra_sugar(
            product.get_ingredients(),
            sugars_total,
            carbohydrate_total,
            ingredient_names
        )

        sugars_total = min(carbohydrate_total, sugars_total + extra_sugar)
        print(f"Total sugars after calculating extra sugar: {sugars_total}g")

    if category == "SAVORY":
        if sugars_total > 3:
            return 4, extra_sugar
        elif 1 <= sugars_total <= 3:
            return 3, extra_sugar
        elif 0.5 <= sugars_total <= 1:
            return 2, extra_sugar
        else:
            return 1, extra_sugar
    else:
        nutriments_total_dm_g = 0
        for nutriment in product.get_nutriments():
            nutriment_name = nutriment.get_nutriment_name()
            if nutriment_name in NUTRIMENTS_DM_EWO:
                nutriments_total_dm_g += nutriment.get_nutriment_value()

        dry_matter_perc = min(max(nutriments_total_dm_g / 100.0, 0.0), 1.0)

        t1 = 2.5 + (5.0 - 2.5) * dry_matter_perc
        t2 = 13.5 + (27.0 - 13.5) * dry_matter_perc
        t3 = 50.0

        if sugars_total <= t1:
            return 1, extra_sugar
        elif sugars_total <= t2:
            return 2, extra_sugar
        elif sugars_total <= t3:
            return 3, extra_sugar
        else:
            return 4, extra_sugar

def calculate_first_step_punctuation(
    ingredients: str,
    product_certifications: list,
    ewo_ingredients: pd.DataFrame
) -> tuple:
    """
    Function that calculates first step of ultraprocessing punctuation.
    Args:
        ingredients (str): Ingredients of the product.
        product_certifications (list): List of product certifications.
        ewo_ingredients (pd.DataFrame): DataFrame with EWO ingredients.

    Returns:
        tuple: First step of ultraprocessing punctuation and ingredients matched.
    """

    ingredients = normalize_text(ingredients)

    # rudimentary_results, items_to_be_ignored = match_ewo_ingredients_rudimentary(
    #     ingredients,
    #     ewo_ingredients,
    #     product_certifications
    # )

    already_matched = match_ewo_ingredients(ingredients, ewo_ingredients, product_certifications)
    items_to_be_ignored = []


    punctuation_items = calculate_punctuation_items_found(already_matched, items_to_be_ignored)

    p2 = punctuation_items[2]
    p3 = punctuation_items[3]
    p4 = punctuation_items[4]

    # Level 4: 4+ MUT3 or 1+ MUT4
    if p3 >= 4 or p4 >= 1:
        return 4, already_matched

    # Level 3: 4+ MUT2 OR (1 to 3 MUT3) -- (and no MUT4)
    if (p2 >= 4 or (1 <= p3 <= 3)) and p4 == 0:
        return 3, already_matched

    # Level 2: 1 to 3 MUT2 -- (and no MUT3 or MUT4)
    if 1 <= p2 <= 3 and p3 == 0 and p4 == 0:
        return 2, already_matched

    # Level 1: Only MUT0 or MUT1 (0 MUT2, 0 MUT3, 0 MUT4)
    return 1, already_matched

def calculate_punctuation_items_found(already_matched: list, items_to_be_ignored: list) -> dict:
    """
    Function to calculate the number of items found in the already matched list.
    Args:
        already_matched (list): List of already matched ingredients.
        items_to_be_ignored (list): List of items to be ignored.

    Returns:
        dict: Dictionary with the number of items found in the already matched list.
    """
    punctuation_items = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }

    for idx, item in enumerate(already_matched):
        if idx not in items_to_be_ignored:
            punctuation_items[item.get_score()] += 1

    return punctuation_items
