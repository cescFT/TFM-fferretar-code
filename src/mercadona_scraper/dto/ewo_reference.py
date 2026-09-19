"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

class EwoReference:
    """
    DTO for EwoReference.
    """
    def __init__(self, ingredient_name: str, reference:str, score: int):
        self.ingredient_name = ingredient_name
        self.reference = reference
        self.score = score

    def get_reference(self) -> str:
        """
        Function to get the reference of the EwoReference.
        Args:
            None.
        Returns:
            str: Reference of the EwoReference.
        """
        return self.reference

    def get_ingredient_name(self) -> str:
        """
        Function to get the ingredient name of the EwoReference.
        Args:
            None.
        Returns:
            str: Ingredient name of the EwoReference.
        """

        return self.ingredient_name

    def get_score(self) -> int:
        """
        Function to get the score of the EwoReference.
        Args:
            None.
        Returns:
            int: Score of the EwoReference.
        """

        return self.score
