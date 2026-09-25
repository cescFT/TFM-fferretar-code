"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from grocery_scraper.dto.ewo_reference import EwoReference
from grocery_scraper.dto.product_nutritional_data import CertificationDTO
import pandas as pd
import re


def match_ewo_ingredients(
        ingredients: str,
        ewo_ingredients: pd.DataFrame,
        product_certifications: list
) -> tuple:
    """
    Function created by myself with the purpose of matching ingredients with EWO ingredients.
    Args:
        ingredients (str): Ingredients to be matched with EWO ingredients.
        ewo_ingredients (pd.DataFrame): EWO ingredients to be matched with.
        product_certifications (list): Product certifications.

    Returns:
        tuple: A tuple containing the already matched ingredients and the items to be ignored because are possible
        contained in other ingredient.
    """

    already_matched = []
    for _, row in ewo_ingredients.iterrows():
        score = int(row['score']) if pd.notna(row['score']) else None

        if score is None:
            continue

        ingredient_names = str(row['es']).strip() if pd.notna(row['es']) else ""
        ingredient_names_splitted = ingredient_names.split(' / ')
        reference_ingredient = str(row['reference']).strip() if pd.notna(row['reference']) else ""
        sugar = row['sugar']

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
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score, sugar)
                    already_matched.append(ewo_reference)
                else:
                    matched = False

            if not matched:
                reference_ingredient = reference_ingredient.replace('-', '')
                pattern_reference_ingredient = r'(?<!\w)' + re.escape(reference_ingredient) + r'(?!\w)'
                if re.search(pattern_reference_ingredient, ingredients):
                    already_exists = check_whether_exists_reference(reference_ingredient, already_matched)
                    if not already_exists:
                        ewo_reference = EwoReference(ingredient_names, reference_ingredient, score, sugar)
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
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score, sugar)
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
                        ewo_reference = EwoReference("zumo concentrado de limon", "", score, False)
                        already_matched.append(ewo_reference)
                else:
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score, True)
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
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score, sugar)
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
                    ewo_reference = EwoReference(ingredient_names, reference_ingredient, score, sugar)
                    already_matched.append(ewo_reference)
            elif re.search(pattern_ingredient_name, ingredients):
                ewo_reference = EwoReference(ingredient_names, reference_ingredient, score, sugar)
                already_matched.append(ewo_reference)

    items_to_be_ignored = []
    ingredient_found: EwoReference
    for idx, ingredient_found in enumerate(already_matched):
        ingredient_name = ingredient_found.get_ingredient_name()
        for ingredient in already_matched:
            if ingredient_name in ingredient.get_ingredient_name() and len(ingredient.get_ingredient_name()) > len(ingredient_name):
                items_to_be_ignored.append(idx)

    return already_matched, items_to_be_ignored


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
