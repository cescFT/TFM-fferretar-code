
constants = {
    "BASIC_URL": "https://tienda.mercadona.es/",
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