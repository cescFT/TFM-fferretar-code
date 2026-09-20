"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from dto.ewo_reference import EwoReference
from dto.product_nutritional_data import ProductNutrimentsDTO, NutrimentDataDTO, CertificationDTO
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

    punctuation_step1 = calculate_first_step_punctuation(
        product.get_ingredients(),
        product.get_certifications(),
        ewo_ingredients
    )
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
    product_certifications: list,
    ewo_ingredients: pd.DataFrame
) -> int:
    """
    Function that calculates first step of ultraprocessing punctuation.
    Args:
        ingredients (str): Ingredients of the product.
        product_certifications (list): List of product certifications.
        ewo_ingredients (pd.DataFrame): DataFrame with EWO ingredients.

    Returns:
        int: First step of ultraprocessing punctuation.
    """

    ingredients = ''.join(
        c for c in unicodedata.normalize('NFD', ingredients)
        if unicodedata.category(c) != 'Mn'
    )

    already_matched = []
    for _, row in ewo_ingredients.iterrows():
        score = int(row['score']) if pd.notna(row['score']) else None

        if score is None:
            continue

        ingredient_names = str(row['es']).strip() if pd.notna(row['es']) else ""
        ingredient_names_splitted = ingredient_names.split(' / ')
        reference_ingredient = str(row['reference']).strip() if pd.notna(row['reference']) else ""

        if reference_ingredient == 'nan':
            reference_ingredient = ""

        ingredient_is_already_found = check_ingredient_already_found(
            reference_ingredient,
            already_matched,
            ingredient_names_splitted
        )

        if ingredient_is_already_found:
            continue

        if reference_ingredient:
            pattern_reference_ingredient = r'(?<!\w)' + re.escape(reference_ingredient) + r'(?!\w)'
            matched = False
            if re.search(pattern_reference_ingredient, ingredients):
                matched = True
                already_exists = check_whether_exists_reference(reference_ingredient, already_matched)
                if not already_exists:
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score)
                    already_matched.append(ewo_reference)
                else:
                    matched = False

            if not matched:
                reference_ingredient = reference_ingredient.replace('-', '')
                pattern_reference_ingredient = r'(?<!\w)' + re.escape(reference_ingredient) + r'(?!\w)'
                if re.search(pattern_reference_ingredient, ingredients):
                    already_exists = check_whether_exists_reference(reference_ingredient, already_matched)
                    if not already_exists:
                        ewo_reference = EwoReference(ingredient_names, reference_ingredient, score)
                        already_matched.append(ewo_reference)
                        matched = True

            if matched:
                continue

        for idx, ingredient_name in enumerate(ingredient_names_splitted):
            if idx != 0:
                ingredient_is_already_found = check_ingredient_already_found(
                    reference_ingredient,
                    already_matched,
                    ingredient_names_splitted
                )

                if ingredient_is_already_found:
                    continue


            pattern_ingredient_name = r'(?<!\w)' + re.escape(ingredient_name) + r'(?!\w)'

            if ingredient_name == "vitaminas_anadidas_no_e":
                pattern = r'(?:^|[,;(])\s*vitaminas?\b'
                if not re.search(pattern, ingredients):
                    continue

                vitamin_positions = re.finditer(pattern, ingredients)
                not_have_vit_e = True
                for match in vitamin_positions:
                    text_after = ingredients[match.end():match.end() + 100]
                    vitamins = re.findall(
                        r'\b(?:a\d{0,2}|b\d{0,2}|c|d\d{0,2}|e|f|k\d{0,2})\b',
                        text_after
                    )

                    if vitamins and 'e' in vitamins:
                        not_have_vit_e = False
                        break

                if not_have_vit_e:
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score)
                    already_matched.append(ewo_reference)

            elif ingredient_name == "zumo_concentrado_no_limon":
                pattern = r'\bzumo\s+concentrado\s+de\s+([^;().]+)'

                has_concentrated_juice_lemon = False
                match: EwoReference
                for match in already_matched:
                    if match.get_ingredient_name() == "zumo concentrado de limon":
                        has_concentrated_juice_lemon = True
                        break

                if not re.search(pattern, ingredients) or has_concentrated_juice_lemon:
                    continue

                juice_positions = re.finditer(pattern, ingredients)
                juices = []

                for match in juice_positions:
                    text_after = match.group(1).strip()
                    fruits = re.split(r'\s*,\s*|\s+y\s+', text_after)
                    for fruit in fruits:
                        fruit = fruit.strip()
                        if fruit:
                            juices.append(fruit)

                if any(juice == 'limon' for juice in juices):
                    has_concentrated_juice_lemon = False
                    match: EwoReference
                    for match in already_matched:
                        if match.get_ingredient_name() == "zumo concentrado de limon":
                            has_concentrated_juice_lemon = True
                            break

                    if not has_concentrated_juice_lemon:
                        score = 0
                        ewo_reference = EwoReference("zumo concentrado de limon", "", score)
                        already_matched.append(ewo_reference)
                else:
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score)
                    already_matched.append(ewo_reference)

            elif ingredient_name == "gluten":
                has_no_gluten_cert = False

                certification: CertificationDTO
                for certification in product_certifications:
                    if certification.get_certification_name() == 'gluten-free':
                        has_no_gluten_cert = True
                        break

                if has_no_gluten_cert:
                    continue

                pattern_no_gluten = r'(?<!\w)' + re.escape("sin gluten") + r'(?!\w)'

                if re.search(pattern_no_gluten, ingredients):
                    continue

                if re.search(pattern_ingredient_name, ingredients):
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score)
                    already_matched.append(ewo_reference)
            elif ingredient_name == "no_harinas_normales":
                if not re.search(r'\bharinas?\b', ingredients):
                    continue

                normal_flour = [
                    "harina de trigo",
                    "harina blanca",
                    "harina semiintegral",
                    "harina integral",
                    "harina semicompleta"
                ]

                normal_flour_already_in_matches = False

                for flour in normal_flour:
                    pattern_ingredient_name = r'(?<!\w)' + re.escape(flour) + r'(?!\w)'
                    if re.search(pattern_ingredient_name, ingredients):
                        normal_flour_already_in_matches = True
                        break

                if not normal_flour_already_in_matches:
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score)
                    already_matched.append(ewo_reference)
            elif re.search(pattern_ingredient_name, ingredients):
                ewo_reference = EwoReference(ingredient_names, reference_ingredient, score)
                already_matched.append(ewo_reference)

    items_to_be_ignored = []
    ingredient_found: EwoReference
    for idx, ingredient_found in enumerate(already_matched):
        ingredient_name = ingredient_found.get_ingredient_name()
        for ingredient in already_matched:
            if ingredient_name in ingredient.get_ingredient_name() and len(ingredient.get_ingredient_name()) > len(ingredient_name):
                items_to_be_ignored.append(idx)

    punctuation_items = calculate_punctuation_items_found(already_matched, items_to_be_ignored)

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

    item: EwoReference
    for item in already_matched:
        if reference_ingredient == item.get_reference():
            return True

    return False

def check_ingredient_already_found(
        reference_ingredient: str,
        already_matched: list,
        ingredient_names_to_check: list
) -> bool:
    """
    Function to check whether ingredient is already found in already matched list.

    Args:
        reference_ingredient (str): Reference of the ingredient if exists (e.g. e-204)
        already_matched (list): List of already matched ingredients.
        ingredient_names_to_check (list): List of ingredient names to check.

    Returns:
        bool: Whether the ingredient is already found in the already matched list.
    """

    if len(already_matched) == 0:
        return False

    if reference_ingredient:
        has_reference_with_hiphen = check_whether_exists_reference(reference_ingredient, already_matched)
        reference_ingredient = reference_ingredient.replace('-', '')
        has_reference_without_hiphen = check_whether_exists_reference(reference_ingredient, already_matched)

        if has_reference_with_hiphen or has_reference_without_hiphen:
            return True

    for current_ingredient_name in ingredient_names_to_check:
        ingredient_already_matched: EwoReference
        for ingredient_already_matched in already_matched:
            ingredients_splitted = ingredient_already_matched.get_ingredient_name().split(" / ")
            if current_ingredient_name in ingredients_splitted:
                return True

    return False

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
