from constants.constants_variables import constants_variables_getter

CONSTANTS_NAME = [
        "BCN_DATA",
        "TGN_DATA",
        "VALLS_DATA"
    ]

def validate(postal_code: str) -> dict|None:

    for constant in CONSTANTS_NAME:
        city_data = constants_variables_getter(constant)
        if city_data['POSTAL_CODE'] == postal_code:
            return city_data

    return None