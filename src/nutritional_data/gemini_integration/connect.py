from dotenv import load_dotenv
from google import genai

def create_connection_to_gemini():
    load_dotenv()

    return genai.Client()
