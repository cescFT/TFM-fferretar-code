"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

constants = {
    "BASIC_URL": "https://tienda.mercadona.es/",
    "BASIC_URL_CATEGORIES": "https://tienda.mercadona.es/categories/112",
    "CIQUAL_URL": "https://ciqual.anses.fr/esearch/aliments/_search",
    "MERCADONA_BASE_URL_API": "https://tienda.mercadona.es/api/products/@@product_id@@/?lang=@@lang@@&wh=@@wh@@",
    "BCN_DATA": {
        "POSTAL_CODE": "08032", # Can Baró -> IST medium
        "WH": "bcn1"
    },
    "MONTFERRI_DATA": {
        "POSTAL_CODE": "43812",
        "WH": "3973"
    },
    "EXCLUDED_CATEGORIES": [
        "Cuidado del cabello",
        "Cuidado facial y corporal",
        "Fitoterapia y parafarmacia",
        "Limpieza y hogar",
        "Maquillaje",
        "Mascotas"
    ],
    "EXCLUDED_SUB_CATEGORIES": [
        "Biberón y chupete",
        "Higiene y cuidado",
        "Toallitas y pañales",
        "Velas y decoración",
        "Hielo"
    ],
    "NOT_INGREDIENTS_SAME_NAME_CATEGORIES": [
        "Fruta y verdura"
    ],
    "LIMIT_PRODUCTS_TO_GET_NUTRITIONAL_DATA": "5",
    "LIMIT_PRODUCTS_TO_GET_NUTRISCORE": "5",
    "LIMIT_PRODUCTS_TO_CALCULATE_ULTRAPROCESSED_PUNCTUATION": "5",
    "BASIC_NUTRIENTS_TO_GET": [
        1,2,3
    ],
    "NUTRIMENT_NO_DATA": "1",
    "NUTRIMENTS_NUTRISCORE": {
        "GENERAL_FOOD": ["Energia", "sucres", "greixos_saturats", "sal", "fibra", "proteines"],
        "RED_MEAT": ["Energia", "sucres", "greixos_saturats", "sal", "fibra", "proteines"],
        "CHEESE": ["Energia", "sucres", "greixos_saturats", "sal", "fibra", "proteines"],
        "FATS_OILS_NUTS_SEEDS": ["greixos_totals", "greixos_saturats", "sucres", "sal", "fibra", "proteines"],
        "BEVERAGES": ["Energia", "sucres", "greixos_saturats", "sal", "fibra", "proteines"],
    },
    "NUTRIMENTS_DM_EWO": ["greixos_totals_g", "hidrats_carboni_g", "fibra_g", "proteines_g", "sal_g"],
    "CERTIFICATIONS_BASIC": [
        1
    ]
}

def constants_variables_getter(key: str) -> str|dict|list:
    """
    Function that gets constants variables by key.

    Args:
        key (str): key of constants variable

    Returns:
        str|dict|list: Constant
    """

    if key not in constants:
        raise Exception(f"Key {key} not found in constants")
    else:
        return constants[key]
