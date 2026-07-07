from dto.product_nutritional_data import ProductNutritionalDataDTO, NutrientDTO


def process_response_from_gemini(
    products_data: list,
    nutritional_data_responses: dict,
    no_data_id: int,
    energy_kcal_id: int,
    energy_kj_id: int,
    nutriments: dict
) -> list:
    nutriments_to_save = []
    for product in products_data:
        product_id = product['id']
        nutritional_data = nutritional_data_responses[product_id]

        product_nutritional_data_dto = ProductNutritionalDataDTO(
            product_id,
            product['id_product'],
            product['category'],
            product['subcategory'],
            product['product_name'],
            product['photo_urls']
        )

        if not nutritional_data:
            no_data_nutriment = NutrientDTO('', 0, '')
            no_data_nutriment.set_nutrient_id(no_data_id)
            product_nutritional_data_dto.nutrients.append(no_data_nutriment)
            print(
                f"No hi ha dades nutricionals per a {product_nutritional_data_dto.get_product_name()} "
                f"({product_nutritional_data_dto.get_mercadona_id()}) en la categoria {product_nutritional_data_dto.get_category()}"
            )
            nutriments_to_save.append(product_nutritional_data_dto)
            continue

        for key, value in nutritional_data.items():
            nutriment_data = NutrientDTO('', 0, '')
            if key == "nutriscore" and value:
                product_nutritional_data_dto.set_nutriscore(value)
                nutriment_data = None
            if key == "energia_kcal" and value:
                nutriment_data.set_nutrient_id(energy_kcal_id)
                nutriment_data.set_nutrient_value(value)
            if key == "energia_kj" and value:
                nutriment_data.set_nutrient_id(energy_kj_id)
                nutriment_data.set_nutrient_value(value)

            if not value:
                continue

            if type(value) == dict:
                name_nutriment = key + "_" + value['units']
                if name_nutriment in nutriments:
                    nutriment_id = nutriments[name_nutriment]
                    nutriment_data.set_nutrient_id(nutriment_id)
                    nutriment_data.set_nutrient_value(value['quantity'])
                else:
                    nutriment_data = NutrientDTO(name_nutriment, value['quantity'], value['units'])

            if nutriment_data:
                product_nutritional_data_dto.add_nutrient(nutriment_data)

        nutriments_to_save.append(product_nutritional_data_dto)

    return nutriments_to_save