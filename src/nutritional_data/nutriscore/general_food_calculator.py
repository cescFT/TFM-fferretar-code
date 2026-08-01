"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

def calculate(
        nutriments:dict,
        is_red_meat: bool = False,
        is_cheese = False
) -> dict:
    """
    Calculates general food nutriscore.

    Args:
        nutriments (dict): Dictionary which have all data necessary to calculate general food nutriscore.
        is_red_meat (bool): If True, calculator adapts proteins for red meat category.
        is_cheese (bool): If True, calculator adapts proteins for cheese category.

    Returns:
        dict: Dictionary with nutriscore result.
    """

    energy = nutriments["Energia"]
    sugars = nutriments["sucres"]
    saturated_fats = nutriments["greixos_saturats"]
    salt = nutriments["sal"]
    fiber = nutriments["fibra"]
    proteins = nutriments["proteines"]
    fruit_percentage = nutriments["fruit_percentage"]

    negative_score = calculate_negative_score(energy, saturated_fats, sugars, salt)
    positive_score = calculate_positive_score(proteins, fiber, fruit_percentage, is_red_meat)

    if negative_score['negative_points'] < 11 or is_cheese:
        nutritional_score = negative_score['negative_points']  - positive_score['positive_points']
    else:
        if positive_score['fruit_percentage_points'] == 5:
            nutritional_score = negative_score['negative_points'] - positive_score['positive_points']
        else:
            nutritional_score = (negative_score['negative_points'] -
                                 (positive_score['fibers_points'] + positive_score['fruit_percentage_points']))

    if nutritional_score <= 0:
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
        'negative_points': negative_score,
        'positive_points': positive_score,
    }

def calculate_positive_score(
        proteins: float,
        fiber: float,
        fruit_percentage: float,
        is_red_meat = False
) -> dict:
    """
    Calculates P part of nutriscore points for general food.

    Args:
        proteins (float): Proteins of the product.
        fiber (float): Fiber of the product.
        fruit_percentage (float): Percentage of fruits of the product.
        is_red_meat (bool): If True, calculator adapts proteins for red meat category.

    Returns:
        dict: Result of the P part.
    """

    p_thresholds = [2.4, 4.8, 7.2, 9.6, 12.0, 14.0, 17.0]
    pts_p = sum(1 for t in p_thresholds if proteins > t)

    if is_red_meat and pts_p > 2:
        pts_p = 2

    f_thresholds = [3.0, 4.1, 5.2, 6.3, 7.4]
    pts_f = sum(1 for t in f_thresholds if fiber > t)

    if fruit_percentage > 80:
        pts_fvl = 5
    elif fruit_percentage > 60:
        pts_fvl = 2
    elif fruit_percentage > 40:
        pts_fvl = 1
    else:
        pts_fvl = 0

    return {
        'positive_points': pts_p + pts_f + pts_fvl,
        'proteins_points': pts_p,
        'fibers_points': pts_f,
        'fruit_percentage_points': pts_fvl
    }


def calculate_negative_score(
        energy: float,
        saturated_fats: float,
        sugars: float,
        salt: float
) -> dict:
    """
    Calculates N part of nutriscore points for general food.

    Args:
        energy (float): Energy of the product.
        saturated_fats (float): Saturated fats of the product.
        sugars (float): Sugars of the product.
        salt (float): Salt of the product.

    Returns:
        dict: Result of the N part.
    """

    e_thresholds = [335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350]
    pts_e = sum(1 for t in e_thresholds if energy > t)

    sf_thresholds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    pts_sf = sum(1 for t in sf_thresholds if saturated_fats > t)

    s_thresholds = [3.4, 6.8, 10, 14, 17, 20, 24, 27, 31, 34, 37, 41, 44, 48, 51]
    pts_s = sum(1 for t in s_thresholds if sugars > t)

    salt_thresholds = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0]
    pts_salt = sum(1 for t in salt_thresholds if salt > t)

    return {
        'negative_points': pts_e + pts_sf + pts_s + pts_salt,
        'energy_points': pts_e,
        'saturated_fats_points': pts_sf,
        'sugar_points': pts_s,
        'salt_points': pts_salt
    }
