"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from dataclasses import dataclass


class EwoReference:
    """
    DTO for EwoReference.
    """
    def __init__(
            self,
            ingredient_name: str,
            reference:str,
            score: int,
            sugar: bool,
            row_id = None,
            span = None
    ):
        self.ingredient_name = ingredient_name
        self.reference = reference
        self.score = score
        self.sugar = sugar
        self.row_id = row_id
        self.span = span

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

    def get_sugar(self) -> bool:
        """
        Function to get the sugar flag of the EwoReference.
        Args:
            None.
        Returns:
            bool: Sugar flag of the EwoReference.
        """

        return self.sugar

@dataclass
class Candidate:
    start: int
    end: int
    priority: int
    ewo_ref: EwoReference

    @property
    def length(self):
        return self.end - self.start
