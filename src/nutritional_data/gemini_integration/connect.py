"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

from dotenv import load_dotenv
from google import genai

def create_connection_to_gemini() -> genai.Client:
    """
    Creates a client Gemini connection object by loading the .env file with
    GEMINI_API_KEY credential.

    Args:
        None.

    Returns:
        genai.Client: Client Gemini connection object.
    """

    load_dotenv()

    return genai.Client()
