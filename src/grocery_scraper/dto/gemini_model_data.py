"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

class GeminiModelDTO:
    """
    Class to represent a Gemini model
    """
    def __init__(self, model_name: str, hours_since_last_petition: int, is_blocked: bool):
        self.model_name = model_name
        self.hours_since_last_petition = hours_since_last_petition
        self.is_blocked = is_blocked == 1

    def get_model_name(self) -> str:
        """
        Returns the name of the Gemini model.

        Args:
            None.

        Returns:
            str: Gemini model name.

        """

        return self.model_name


    def get_hours_since_last_petition(self) -> int:
        """
        Function to get the hours since last petition.

        Args:
            None.

        Returns:
            int: hours since last petition.
        """

        return self.hours_since_last_petition

    def get_is_blocked(self) -> bool:
        """
        Function to get if gemini model is blocked.

        Args:
            None.

        Returns:
            bool: True if gemini model is blocked.
        """

        return self.is_blocked

    def set_is_blocked(self, is_blocked: bool) -> None:
        """
        Function to set if gemini model is blocked.
        Args:
            is_blocked: Boolean to set if gemini model is blocked.

        Returns:
            None.
        """

        self.is_blocked = is_blocked
