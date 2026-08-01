"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

import math


def calculate(nutriments:dict) -> dict:
    """
    Calculates fats, oils, nuts and seeds nutriscore.

    Args:
        nutriments (dict): Dictionary which have all data necessary to calculate fats, oils, nuts and seeds nutriscore.

    Returns:
        dict: Dictionary with nutriscore result.
    """

    total_fats = nutriments["greixos_totals"]
    saturated_fats = nutriments["greixos_saturats"]
    ratio_sfa = (
        saturated_fats / total_fats * 100
        if total_fats > 0
        else 0
    )

    ratio_sfa = round(ratio_sfa, 1)

    energy_from_saturates = math.ceil(saturated_fats * 37)
    sugars = nutriments["sucres"]
    salt = nutriments["sal"]
    fiber = nutriments["fibra"]
    proteins = nutriments["proteines"]
    fruit_percentage = nutriments["fruit_percentage"]

    negative_points = calculate_negative_points(energy_from_saturates, sugars, ratio_sfa, salt)
    positive_points = calculate_positive_points(proteins, fiber, fruit_percentage)

    if negative_points["negative_points"] < 7:
        nutritional_score = negative_points["negative_points"] - positive_points["positive_points"]
    else:
        nutritional_score = (negative_points["negative_points"] -
                             (positive_points["fiber_points"] + positive_points["fruit_points"]))

    if nutritional_score <= -6:
        letter = "A"
    elif nutritional_score <= 2:
        letter = "B"
    elif nutritional_score <= 10:
        letter = "C"
    elif nutritional_score <= 18:
        letter = "D"
    else:
        letter = "E"

    return {
        'letter': letter,
        'points': nutritional_score,
        'negative_points': negative_points,
        'positive_points': positive_points,
    }

def calculate_positive_points(
        proteins: float,
        fiber: float,
        fruit_percentage: float,
) -> dict:
    """
    Calculates P part of nutriscore points for fats, oils, nuts and seeds.

    Args:
        proteins (float): Proteins of the product.
        fibres (float): Fibres of the product.
        fruit_percentage (float): Percentage of fruits of the product.

    Returns:
        dict: Result of the P part.
    """


    proteins_thresholds = [2.4, 4.8, 7.2, 9.6, 12.0, 14.0, 17.0]
    pnt_proteins = sum(1 for t in proteins_thresholds if proteins > t)

    fiber_thresholds = [3, 4.1, 5.2, 6.3, 7.4]
    pnt_fiber = sum(1 for t in fiber_thresholds if fiber > t)

    if fruit_percentage > 80:
        pnt_fruit_percentage = 5
    elif fruit_percentage > 60:
        pnt_fruit_percentage = 2
    elif fruit_percentage > 40:
        pnt_fruit_percentage = 1
    else:
        pnt_fruit_percentage = 0

    return {
        "positive_points": pnt_proteins + pnt_fiber + pnt_fruit_percentage,
        "protein_points": pnt_proteins,
        "fiber_points": pnt_fiber,
        "fruit_points": pnt_fruit_percentage,
    }


def calculate_negative_points (
        energy_from_saturates: float,
        sugars: float,
        ratio_sfa: float,
        salt: float
) -> dict:
    """
    Calculates N part of nutriscore points for fats, oils, nuts and seeds.

    Args:
        energy_from_saturates (float): Energy from saturates of the product.
        sugars (float): Sugars of the product.
        ratio_sfa (float): saturated_fats / total_fats.
        salt (float): Salt of the product.

    Returns:
        dict: Result of the N part.
    """

    energy_from_saturates_thresholds = [120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200]
    pnt_energy = sum(1 for t in energy_from_saturates_thresholds if energy_from_saturates > t)

    sugars_thresholds = [3.4, 6.8, 10, 14, 17, 20, 24, 27, 31, 34, 37, 41, 44, 48, 51]
    pnt_sugars = sum(1 for t in sugars_thresholds if sugars > t)

    ratio_sfa_thesholds = [10, 16, 22, 28, 34, 40, 46, 52, 58, 64]

    pnt_sfa = sum(1 for t in ratio_sfa_thesholds if t < ratio_sfa)
    if ratio_sfa >= 64:
        pnt_sfa += 1

    salt_thresholds = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8, 3, 3.2, 3.4, 3.6, 3.8, 4]
    pnt_salt = sum(1 for t in salt_thresholds if salt > t)


    return {
        "negative_points": pnt_energy + pnt_sugars + pnt_sfa + pnt_salt,
        "energy_from_saturates_points": pnt_energy,
        "sugars_points": pnt_sugars,
        "ratio_sfa_points": pnt_sfa,
        "salt_points": pnt_salt,
    }
