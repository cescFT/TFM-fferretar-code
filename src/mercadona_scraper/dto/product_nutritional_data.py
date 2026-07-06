class ProductNutritionalDataDTO:
    def __init__(
            self,
            id: int,
            mercadona_id: str,
            category: str,
            subcategory: str,
            product_name: str,
            photos: list,
    ):
        self.id = id
        self.mercadona_id = mercadona_id
        self.category = category
        self.subcategory = subcategory
        self.product_name = product_name
        self.photos = photos
        self.nutrients = []
        self.nutriscore = None


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

    def add_nutrient(self, nutrient):
        self.nutrients.append(nutrient)

    def get_nutriscore(self):
        return self.nutriscore

    def set_nutriscore(self, nutriscore: str):
        self.nutriscore = nutriscore

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