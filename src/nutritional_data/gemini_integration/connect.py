from dotenv import load_dotenv
from google import genai

def create_connection_to_gemini() -> genai.Client:
    load_dotenv()

    return genai.Client()
