"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

class CiqualDTO:
    """
    DTO class that saves ciqual information.
    """
    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text

    def get_id(self) -> str:
        """
        Function that returns ciqual id

        Args:
            None.

        Returns:
            str: ciqual id
        """

        return self.id

    def get_text(self) -> str:
        """
        Function that returns ciqual text

        Args:
            None.

        Returns:
            str: ciqual text
        """

        return self.text

class NutrientDTO:
    """
    DTO class that saves nutrient information to persist in database
    """
    def __init__(self, nutrient_name: str, nutrient_value: float, nutrient_unit: str):
        self.nutrient_name = nutrient_name
        self.nutrient_value = nutrient_value
        self.nutrient_unit = nutrient_unit
        self.nutrient_id = None


    def get_nutrient_name(self) -> str:
        """
        Function that returns nutrient name

        Args:
            None.

        Returns:
            str: nutrient name
        """

        return self.nutrient_name

    def get_nutrient_value(self) -> float:
        """
        Function that returns nutrient value.

        Args:
            None.

        Returns:
            float: nutrient value
        """

        return self.nutrient_value

    def get_nutrient_unit(self) -> str:
        """
        Function that returns nutrient unit.

        Args:
            None.

        Returns:
             str: Nutrient unit.
        """

        return self.nutrient_unit

    def get_nutrient_id(self) -> int|None:
        """
        Function that returns nutrient id.

        Args:
            None.

        Returns:
             int|None: Nutrient id
        """

        return self.nutrient_id

    def set_nutrient_id(self, nutrient_id: int|None = None) -> None:
        """
        Function set nutrient id.

        Args:
            nutrient_id (int|None): Nutrient id.

        Returns:
            None.
        """

        self.nutrient_id = nutrient_id

    def set_nutrient_value(self, nutrient_value: float) -> None:
        """
        Function set nutrient value.

        Args:
            nutrient_value (float): Nutrient value.

        Returns:
            None.
        """

        self.nutrient_value = nutrient_value

class CertificationDTO:
    """
    DTO class that saves certification information to persist in database.
    """
    def __init__(self, certification_name: str, certification_id: int|None = None):
        self.certification_name = certification_name
        self.certification_id = certification_id

    def get_certification_name(self) -> str:
        """
        Function that returns certification name.

        Args:
            None.

        Returns:
            str: Certification name.
        """

        return self.certification_name

    def get_certification_id(self) -> int|None:
        """
        Function that returns certification id.

        Args:
            None.

        Returns:
            int|None: Certification id.
        """

        return self.certification_id

    def set_certification_id(self, certification_id: int|None) -> None:
        """
        Function set certification id.

        Args:
            certification_id (int|None): Certification id.

        Returns:
            None.
        """

        self.certification_id = certification_id

class ProductNutritionalDataDTO:
    """
    DTO class that represents product nutritional data not saved in database.
    """
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


    def get_id(self) -> int:
        """
        Function that returns product id.

        Args:
            None.

        Returns:
            int: product id.
        """

        return self.id

    def get_product_name(self) -> str:
        """
        Function that returns product name.

        Args:
            None.

        Returns:
            str: product name.
        """

        return self.product_name

    def get_mercadona_id(self) -> str:
        """
        Function that retrieves mercadona id.

        Args:
            None.

        Returns:
            str: Mercadona id.
        """

        return self.mercadona_id

    def get_category(self) -> str:
        """
        Function get category.

        Args:
            None.

        Returns:
            str: product category.
        """

        return self.category

    def get_subcategory(self) -> str:
        """
        Function get subcategory.

        Args:
            None.

        Returns:
             str: product subcategory.
        """

        return self.subcategory

    def get_product_photos(self) -> list:
        """
        Function get photos from product.

        Args:
            None.

        Returns:
            list: List of product photos.
        """

        return self.photos

    def get_nutrients(self) -> list:
        """
        Function that gets nutriments.

        Args:
             None.

        Returns:
            list: List of nutriments.
        """
        return self.nutrients

    def add_nutrient(self, nutrient: NutrientDTO) -> None:
        """
        Function that append new nutriment in product.

        Args:
            nutrient (NutrientDTO): Nutrient to add.

        Returns:
            None.
        """

        self.nutrients.append(nutrient)

    def get_nutriscore(self) -> str|None:
        """
        Function to get nutriscore of product.

        Args:
            None.

        Returns:
            str|None: Nutriscore.
        """

        return self.nutriscore

    def get_origin(self) -> str:
        """
        Function to get origin of product.

        Args:
            None.

        Returns:
             str: Origin of product.
        """

        return self.origin

    def set_nutriscore(self, nutriscore: str) -> None:
        """
        Function to set nutriscore of product.

        Args:
            nutriscore (str): Nutriscore.

        Returns:
             None.
        """

        self.nutriscore = nutriscore

    def set_origin_from_gemini(self, origin_from_gemini: str) -> None:
        """
        Function to set origin extracted from gemini.

        Args:
            origin_from_gemini (str): Origin extracted from gemini.

        Returns:
            None.
        """

        self.origin_from_gemini = origin_from_gemini

    def get_origin_from_gemini(self) -> str:
        """
        Function get origin from gemini.

        Args:
            None.

        Returns:
             str: Origin extracted from gemini.
        """

        return self.origin_from_gemini

    def add_certifications(self, certification: CertificationDTO) -> None:
        """
        Function append certifications found.

        Args:
            certification (CertificationDTO): Certification found.

        Returns:
            None.
        """

        self.certifications.append(certification)

    def get_certifications(self) -> list:
        """
        Function to get certifications.

        Args:
            None.

        Returns:
            list: Certifications.
        """

        return self.certifications

    def get_ciqual_response(self) -> CiqualDTO:
        """
        Function get ciqual response.

        Args:
            None.

        Returns:
             CiqualDTO: Ciqual response.
        """

        return self.ciqual_response

    def set_ciqual_response(self, ciqual_response:CiqualDTO) -> None:
        """
        Function to set ciqual response.

        Args:
            ciqual_response: Ciqual response.

        Returns:
             None.
        """

        self.ciqual_response = ciqual_response

class NutrimentDataDTO:
    """
    DTO class for nutriments already saved into database.
    """
    def __init__(self, nutriment_id: int, nutriment_name: str, nutriment_value: float, nutriment_unit: str):
        self.nutriment_id = nutriment_id
        self.nutriment_name = nutriment_name
        self.nutriment_value = nutriment_value
        self.nutriment_unit = nutriment_unit

    def get_nutriment_id(self) -> int:
        """
        Function get nutriment id.

        Args:
            None.

        Returns:
             int: Nutriment id.
        """

        return self.nutriment_id

    def get_nutriment_name(self) -> str:
        """
        Function get nutriment name.

        Args:
            None.

        Returns:
             str: Nutriment name.
        """

        return self.nutriment_name

    def get_nutriment_value(self) -> float:
        """
        Function get nutriment value.

        Args:
            None.

        Returns:
             float: Nutriment value.
        """

        return self.nutriment_value

    def get_nutriment_unit(self) -> str:
        """
        Function get nutriment unit.

        Args:
            None.

        Returns:
             str: Nutriment unit.
        """

        return self.nutriment_unit

class ProductNutrimentsDTO:
    """
    DTO class for product and nutriments already saved into database.
    """
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

    def get_id(self) -> int:
        """
        Function get product id.

        Args:
            None.

        Returns:
             int: Product id.
        """

        return self.id

    def get_mercadona_id(self) -> int:
        """
        Function get mercadona id.

        Args:
            None.

        Returns:
             int: Mercadona id.
        """

        return self.id_product

    def get_category(self) -> str:
        """
        Function get product category.

        Args:
            None.

        Returns:
             str: Product category.
        """

        return self.category

    def get_subcategory(self) -> str:
        """
        Function get subcategory.

        Args:
            None.

        Returns:
             str: Product subcategory.
        """

        return self.subcategory

    def get_second_subcategory(self) -> str:
        """
        Function get second subcategory.

        Args:
            None.

        Returns:
             str: Product second subcategory.
        """

        return self.second_subcategory

    def get_product_name(self) -> str:
        """
        Function get product name.

        Args:
            None.

        Returns:
             str: Product name.
        """

        return self.product_name

    def get_ingredients(self) -> str:
        """
        Function get ingredients.

        Args:
            None.

        Returns:
             str: Ingredients.
        """

        return self.ingredients

    def get_alcohol_grades(self) -> float:
        """
        Function get alcohol grades.

        Args:
            None.

        Returns:
             float: Alcohol grades.
        """

        return self.alcohol_grades

    def get_nutriments(self) -> list:
        """
        Function get nutriments.

        Args:
            None.

        Returns:
             list: Nutriments.
        """

        return self.nutriments
