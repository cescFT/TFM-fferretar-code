import re


def calculate(nutriments: dict) -> dict:
    energy = nutriments["Energia"]
    sugars = nutriments["sucres"]
    saturated_fats = nutriments["greixos_saturats"]
    salt = nutriments["sal"]
    ingredients = nutriments["ingredients"]
    fiber = nutriments["fibra"]
    proteins = nutriments["proteines"]
    fruit_percentage = nutriments["fruit_percentage"]

    has_presence_of_non_nutritive_sweeteners = check_presence_of_non_nutritive_sweeteners(ingredients)

    negative_score = calculate_negative_score(
        energy,
        sugars,
        saturated_fats,
        salt,
        has_presence_of_non_nutritive_sweeteners
    )

    positive_score = calculate_positive_score(proteins, fiber, fruit_percentage)

    nutritional_score = negative_score['negative_points'] - positive_score['positive_points']

    if nutritional_score <= 2:
        letter = "B"
    elif nutritional_score <= 6:
        letter = "C"
    elif nutritional_score <= 9:
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
        fibres: float,
        fruit_percentage: float
) -> dict:
    proteins_thresholds = [1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3]
    pnt_p = sum(1 for t in proteins_thresholds if proteins > t)

    fibers_thresholds = [3, 4.1, 5.2, 6.3, 7.4]
    pnt_f = sum(1 for t in fibers_thresholds if fibres > t)

    pnt_fruit = 0
    if fruit_percentage > 80:
        pnt_fruit = 6
    elif fruit_percentage > 60:
        pnt_fruit = 4
    elif fruit_percentage > 40:
        pnt_fruit = 2

    return {
        "positive_points": pnt_p + pnt_f + pnt_fruit,
        "proteins_score": pnt_p,
        "fiber_score": pnt_f,
        "fruit_percentage_score": pnt_fruit,
    }



def calculate_negative_score(
        energy: float,
        sugars: float,
        saturated_fats: float,
        salt: float,
        has_non_nutritive_sweeteners: bool
) -> dict:
    energy_thresholds = [30, 90, 150, 210, 240, 270, 300, 330, 360, 390]

    pnt_e = None
    for points, t in enumerate(energy_thresholds):
        if energy <= t:
            pnt_e = points
            break

    if not pnt_e:
        pnt_e = 10

    sugars_thresholds = [0.5, 2, 3.5, 5, 6, 7, 8, 9, 10, 11]
    pnt_s = None

    for points, t in enumerate(sugars_thresholds):
        if sugars <= t:
            pnt_s = points
            break

    if not pnt_s:
        pnt_s = 10


    saturated_fats_thresholds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    pnt_f = sum(1 for t in saturated_fats_thresholds if saturated_fats > t)

    salt_thresholds = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8, 3, 3.2, 3.4, 3.6, 3.8, 4]
    pnt_salt = sum(1 for t in salt_thresholds if salt > t)

    pnt_presence_of_non_nutritive_sweeteners = 0
    if has_non_nutritive_sweeteners:
        pnt_presence_of_non_nutritive_sweeteners = 4

    return {
        "negative_points": pnt_e + pnt_s + pnt_f + pnt_salt + pnt_presence_of_non_nutritive_sweeteners,
        "energy_score": pnt_e,
        "sugars_score": pnt_s,
        "saturated_fats_score": pnt_f,
        "salt_score": pnt_salt,
        "non_sweeteners_score": pnt_presence_of_non_nutritive_sweeteners,
    }




def check_presence_of_non_nutritive_sweeteners(ingredients: str|None) -> bool:
    if not ingredients:
        return False

    ingredients = ingredients.lower()

    NNS_REGEX = re.compile(
        r"\b(?:"
        # E-numbers
        r"e\s*-?\s*(?:420|421|953|956|964|965|966|967|968)"
        r"|"
        # Names
        r"sorbitol(?:s)?"
        r"|mannitol"
        r"|isomalt"
        r"|alitame"
        r"|polyglycitol(?:\s+syrup)?"
        r"|maltitol(?:s)?"
        r"|lactitol"
        r"|xylitol"
        r"|erythritol"
        r")\b",
        re.IGNORECASE
    )

    return bool(NNS_REGEX.search(ingredients))