
constants = {
    "BASIC_URL": "https://tienda.mercadona.es/",
    "MERCADONA_BASE_URL_API": "https://tienda.mercadona.es/api/products/@@product_id@@/?lang=es&wh=@@wh@@",
    "BCN_DATA": {
        "POSTAL_CODE": "08017",
        "WH": "bcn1"
    },
    "TGN_DATA": {
        "POSTAL_CODE": "43007",
        "WH": "4074"
    },
    "VALLS_DATA": {
        "POSTAL_CODE": "43800",
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
        "Toallitas y pañales"
    ],
    "NOT_INGREDIENTS_SAME_NAME_CATEGORIES": [
        "Fruta y verdura"
    ],
    "LIMIT_PRODUCTS_TO_GET_NUTRITIONAL_DATA": "5",
    "BASIC_NUTRIENTS_TO_GET": [
        1,2,3
    ]
}

def constants_variables_getter(key: str) -> str|dict:
    """

    :return:
    """

    if key not in constants:
        raise Exception(f"Key {key} not found in constants")
    else:
        return constants[key]