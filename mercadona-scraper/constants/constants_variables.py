
constants = {
    "BASIC_URL": "https://tienda.mercadona.es/",
    "MERCADONA_BASE_URL_API": "https://tienda.mercadona.es/api/products/@@product_id@@/?lang=es&wh=3973", # TODO FER CODI PER CANVIAR EL WH en funció del codi postal
    "POSTAL_CODE_BCN": "08017",
    "POSTAL_CODE_TGN": "43007",
    "POSTAL_CODE_VALLS": "43800",
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
        "Toallitas y pañales"
    ],
    "EXCLUDED_CATEGORIES_TO_GET_NUTRITIONAL_SCORE": [
        "Fruta y verdura"
    ],
    "NOT_INGREDIENTS_SAME_NAME_CATEGORIES": [
        "Fruta y verdura"
    ]
}

def get_all_constants() -> dict:
    return constants

def constants_variables_getter(key: str) -> str:
    """

    :return:
    """

    if key not in constants:
        raise Exception(f"Key {key} not found in constants")
    else:
        return constants[key]