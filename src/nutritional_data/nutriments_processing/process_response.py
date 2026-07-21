from dto.product_nutritional_data import ProductNutritionalDataDTO, NutrientDTO, CiqualDTO, CertificationDTO


def add_no_nutrients_data(
    product_nutritional_data_dto: ProductNutritionalDataDTO,
    no_data_id: int
) -> ProductNutritionalDataDTO:
    no_data_nutriment = NutrientDTO('', 0, '')
    no_data_nutriment.set_nutrient_id(no_data_id)
    product_nutritional_data_dto.add_nutrient(no_data_nutriment)

    return product_nutritional_data_dto


def process_response_from_gemini(
    products_data: list,
    nutritional_data_responses: dict,
    no_data_id: int,
    energy_kcal_id: int,
    energy_kj_id: int,
    nutriments: dict,
    no_certification_id: int,
    certifications: dict
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
            product['photo_urls'],
            product['origin']
        )

        # afegir també el tema del nutriscore...



        if not nutritional_data:
            product_nutritional_data_dto = add_no_nutrients_data(product_nutritional_data_dto, no_data_id)
            print(
                f"No hi ha dades nutricionals per a {product_nutritional_data_dto.get_product_name()} "
                f"({product_nutritional_data_dto.get_mercadona_id()}) en la categoria {product_nutritional_data_dto.get_category()}"
            )
            nutriments_to_save.append(product_nutritional_data_dto)
            continue

        for key, value in nutritional_data.items():
            nutriment_data = NutrientDTO('', 0, '')
            process_dict_as_nutriment = True
            if key == "origen" and value:
                product_nutritional_data_dto.set_origin_from_gemini(value)
                nutriment_data = None
            if key == "ciqual_data" and value:
                ciqual_data = CiqualDTO(value['id'], value['text'])
                product_nutritional_data_dto.set_ciqual_response(ciqual_data)
                nutriment_data = None
                process_dict_as_nutriment = False
            if key == "certifications":
                if not value:
                    certification_dto = CertificationDTO('', no_certification_id)
                    product_nutritional_data_dto.add_certifications(certification_dto)
                else:
                    for certification in value:
                        certification_dto = CertificationDTO(certification)
                        if certification in certifications:
                            certification_id = certifications[certification]
                        else:
                            certification_id = None
                        certification_dto.set_certification_id(certification_id)
                        product_nutritional_data_dto.add_certifications(certification_dto)
                nutriment_data = None
            if key == "energia_kcal" and value:
                nutriment_data.set_nutrient_id(energy_kcal_id)
                nutriment_data.set_nutrient_value(value)
            if key == "energia_kj" and value:
                nutriment_data.set_nutrient_id(energy_kj_id)
                nutriment_data.set_nutrient_value(value)

            if not value:
                continue

            if type(value) == dict and process_dict_as_nutriment:
                name_nutriment = key + "_" + value['units']
                if name_nutriment in nutriments:
                    nutriment_id = nutriments[name_nutriment]
                    nutriment_data.set_nutrient_id(nutriment_id)
                    nutriment_data.set_nutrient_value(value['quantity'])
                else:
                    nutriment_data = NutrientDTO(name_nutriment, value['quantity'], value['units'])

            if nutriment_data:
                product_nutritional_data_dto.add_nutrient(nutriment_data)

        if not product_nutritional_data_dto.get_nutrients():
            product_nutritional_data_dto = add_no_nutrients_data(product_nutritional_data_dto, no_data_id)
            print(
                f"No hi ha dades nutricionals per a {product_nutritional_data_dto.get_product_name()} "
                f"({product_nutritional_data_dto.get_mercadona_id()}) en la categoria {product_nutritional_data_dto.get_category()}"
            )

        nutriments_to_save.append(product_nutritional_data_dto)

    return nutriments_to_save