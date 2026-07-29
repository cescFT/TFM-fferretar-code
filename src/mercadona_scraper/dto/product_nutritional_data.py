class CiqualDTO:
    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text

    def get_id(self):
        return self.id

    def get_text(self):
        return self.text

class NutrientDTO:
    def __init__(self, nutrient_name: str, nutrient_value: float, nutrient_unit: str):
        self.nutrient_name = nutrient_name
        self.nutrient_value = nutrient_value
        self.nutrient_unit = nutrient_unit
        self.nutrient_id = None


    def get_nutrient_name(self):
        return self.nutrient_name

    def get_nutrient_value(self):
        return self.nutrient_value

    def get_nutrient_unit(self):
        return self.nutrient_unit

    def get_nutrient_id(self):
        return self.nutrient_id

    def set_nutrient_id(self, nutrient_id: int|None = None):
        self.nutrient_id = nutrient_id

    def set_nutrient_value(self, nutrient_value: float):
        self.nutrient_value = nutrient_value

class CertificationDTO:
    def __init__(self, certification_name: str, certification_id: int|None = None):
        self.certification_name = certification_name
        self.certification_id = certification_id

    def get_certification_name(self):
        return self.certification_name

    def get_certification_id(self):
        return self.certification_id

    def set_certification_id(self, certification_id: int|None):
        self.certification_id = certification_id

class ProductNutritionalDataDTO:
    def __init__(
            self,
            id: int,
            mercadona_id: str,
            category: str,
            subcategory: str,
            product_name: str,
            photos: list,
            origin: str,
    ):
        self.id = id
        self.mercadona_id = mercadona_id
        self.category = category
        self.subcategory = subcategory
        self.product_name = product_name
        self.photos = photos
        self.origin = origin
        self.ciqual_response = None
        self.nutrients = []
        self.nutriscore = None
        self.origin_from_gemini = None
        self.certifications = []


    def get_id(self):
        return self.id

    def get_product_name(self):
        return self.product_name

    def get_mercadona_id(self):
        return self.mercadona_id

    def get_category(self):
        return self.category

    def get_subcategory(self):
        return self.subcategory

    def get_product_photos(self):
        return self.photos

    def get_nutrients(self):
        return self.nutrients

    def add_nutrient(self, nutrient: NutrientDTO):
        self.nutrients.append(nutrient)

    def get_nutriscore(self):
        return self.nutriscore

    def get_origin(self):
        return self.origin

    def set_nutriscore(self, nutriscore: str):
        self.nutriscore = nutriscore

    def set_origin_from_gemini(self, origin_from_gemini: str):
        self.origin_from_gemini = origin_from_gemini

    def get_origin_from_gemini(self):
        return self.origin_from_gemini

    def add_certifications(self, certification: CertificationDTO):
        self.certifications.append(certification)

    def get_certifications(self):
        return self.certifications

    def get_ciqual_response(self):
        return self.ciqual_response

    def set_ciqual_response(self, ciqual_response:CiqualDTO):
        self.ciqual_response = ciqual_response

class NutrimentDataDTO:
    def __init__(self, nutriment_id: int, nutriment_name: str, nutriment_value: float, nutriment_unit: str):
        self.nutriment_id = nutriment_id
        self.nutriment_name = nutriment_name
        self.nutriment_value = nutriment_value
        self.nutriment_unit = nutriment_unit

    def get_nutriment_id(self):
        return self.nutriment_id

    def get_nutriment_name(self):
        return self.nutriment_name

    def get_nutriment_value(self):
        return self.nutriment_value

    def get_nutriment_unit(self):
        return self.nutriment_unit

class ProductNutrimentsDTO:
    def __init__(
            self,
            id: int,
            id_product: int,
            category: str,
            subcategory: str,
            second_subcategory: str,
            product_name: str,
            ingredients: str,
            alcohol_grades: float,
            nutriments: list
    ):
        self.id = id
        self.id_product = id_product
        self.category = category
        self.subcategory = subcategory
        self.second_subcategory = second_subcategory
        self.product_name = product_name
        self.ingredients = ingredients
        self.alcohol_grades = alcohol_grades
        self.nutriments = []
        for nutriment in nutriments:
            self.nutriments.append(
                NutrimentDataDTO(
                    nutriment['id_nutriment'],
                    nutriment['nutriment_name'],
                    nutriment['quantity'],
                    nutriment['units']
                )
            )


    def get_id(self):
        return self.id

    def get_mercadona_id(self):
        return self.id_product

    def get_category(self):
        return self.category

    def get_subcategory(self):
        return self.subcategory

    def get_second_subcategory(self):
        return self.second_subcategory

    def get_product_name(self):
        return self.product_name

    def get_ingredients(self):
        return self.ingredients

    def get_alcohol_grades(self):
        return self.alcohol_grades

    def get_nutriments(self):
        return self.nutriments
