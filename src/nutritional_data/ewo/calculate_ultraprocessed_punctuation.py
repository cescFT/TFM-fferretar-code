"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from dto.product_nutritional_data import ProductNutrimentsDTO, NutrimentDataDTO
from nutritional_data.ewo.parse_mercadona_categories_to_ewo_categories import parse
from mercadona_scraper.constants.constants_variables import constants_variables_getter
import pandas as pd
import unicodedata
import re

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
          product.get_mercadona_id(), " ", product.get_product_name()
    )

    category = parse(product)

    print("Category calculated: ", category)

    if not product.get_ingredients() or not category:
        print(f"The product {product.get_mercadona_id()} {product.get_product_name()} has directly a good punctuation.")
        return {'qualification': "1"}

    punctuation_step1 = calculate_first_step_punctuation(product.get_ingredients(), ewo_ingredients)
    punctuation_step2 = calculate_second_step_punctuation(product, category)

    qualification = calculate_third_step_punctuation(punctuation_step1, punctuation_step2)

    punct_dict = {
        'step1': str(punctuation_step1),
        'step2': str(punctuation_step2),
        'qualification': str(qualification),
        'category': category
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
    category: str
) -> int:
    """
    Function that calculates second step of ultraprocessing punctuation.
    Args:
        product (ProductNutrimentsDTO): Product to calculate ultraprocessed punctuation.
        category (str): Category of the product.

    Returns:
        int: Second step of ultraprocessing punctuation.
    """
    nutriments = product.get_nutriments()

    sugars_total = 0
    nutriment: NutrimentDataDTO
    for nutriment in nutriments:
        if nutriment.get_nutriment_name() == "sucres_g":
            sugars_total = nutriment.get_nutriment_value()
            break

    if category == "SAVORY":
        if sugars_total > 3:
            return 4
        elif 1 <= sugars_total <= 3:
            return 3
        elif 0.5 <= sugars_total <= 1:
            return 2
        else:
            return 1
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
            return 1
        elif sugars_total <= t2:
            return 2
        elif sugars_total <= t3:
            return 3
        else:
            return 4


def calculate_first_step_punctuation(
    ingredients: str,
    ewo_ingredients: pd.DataFrame
) -> int:
    """
    Function that calculates first step of ultraprocessing punctuation.
    Args:
        ingredients (str): Ingredients of the product.
        ewo_ingredients (pd.DataFrame): DataFrame with EWO ingredients.

    Returns:
        int: First step of ultraprocessing punctuation.
    """

    punctuation_items = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }

    ingredients = ''.join(
        c for c in unicodedata.normalize('NFD', ingredients)
        if unicodedata.category(c) != 'Mn'
    )

    already_matched = []
    for _, row in ewo_ingredients.iterrows():
        ingredient_name = str(row['es']).strip() if pd.notna(row['es']) else ""
        reference_ingredient = str(row['reference']).strip() if pd.notna(row['reference']) else ""
        score = int(row['score']) if pd.notna(row['score']) else None

        if score is None:
            continue

        matched = False
        pattern_ingredient_name = r'(?<!\w)' + re.escape(ingredient_name) + r'(?!\w)'
        pattern_reference_ingredient = r'(?<!\w)' + re.escape(reference_ingredient) + r'(?!\w)'

        if re.search(pattern_ingredient_name, ingredients) and not ingredient_name in already_matched:
            matched = True
            already_matched.append(ingredient_name)
        elif reference_ingredient and reference_ingredient != 'nan':
            if re.search(pattern_reference_ingredient, ingredients) and not reference_ingredient in already_matched:
                matched = True
                already_exists = check_whether_exists_reference(reference_ingredient, already_matched)
                if not already_exists:
                    already_matched.append(reference_ingredient)
                else:
                    matched = False

            if not matched:
                reference_ingredient = reference_ingredient.replace('-', '')
                pattern_reference_ingredient = r'(?<!\w)' + re.escape(reference_ingredient) + r'(?!\w)'
                if re.search(pattern_reference_ingredient, ingredients) and not reference_ingredient in already_matched:
                    matched = True
                    already_exists = check_whether_exists_reference(reference_ingredient, already_matched)
                    if not already_exists:
                        already_matched.append(reference_ingredient)
                    else:
                        matched = False


        if matched:
            punctuation_items[score] += 1

    p2 = punctuation_items[2]
    p3 = punctuation_items[3]
    p4 = punctuation_items[4]

    # Level 4: 4+ MUT3 or 1+ MUT4
    if p3 >= 4 or p4 >= 1:
        return 4

    # Level 3: 4+ MUT2 OR (1 to 3 MUT3) -- (and no MUT4)
    if (p2 >= 4 or (1 <= p3 <= 3)) and p4 == 0:
        return 3

    # Level 2: 1 to 3 MUT2 -- (and no MUT3 or MUT4)
    if 1 <= p2 <= 3 and p3 == 0 and p4 == 0:
        return 2

    # Level 1: Only MUT0 or MUT1 (0 MUT2, 0 MUT3, 0 MUT4)
    return 1

def check_whether_exists_reference(reference_ingredient: str, already_matched: list) -> bool:
    """
    Function that checks if reference is in already matched list to not repeat it.

    Args:
        reference_ingredient (str): Reference ingredient to check.
        already_matched (list): List of already matched ingredients.

    Returns:
        bool: True if reference ingredient is in already matched list, False otherwise.
    """
    if '-' in reference_ingredient:
        reference_ingredient = reference_ingredient.replace('-', '')
    else:
        reference_ingredient = re.sub(r'^e', 'e-', reference_ingredient)

    for item in already_matched:
        if reference_ingredient == item:
            return True

    return False
