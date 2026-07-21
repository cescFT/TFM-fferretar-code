from constants.constants_variables import constants_variables_getter

CONSTANTS_NAME = [
        "BCN_DATA",
        "MONTFERRI_DATA"
    ]

def validate(postal_code: str) -> dict:

    for constant in CONSTANTS_NAME:
        city_data = constants_variables_getter(constant)
        if city_data['POSTAL_CODE'] == postal_code:
            return city_data

    raise Exception("Postal code info not found")