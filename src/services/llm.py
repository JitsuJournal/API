# System
import os
from dotenv import load_dotenv
# Local 
# Third Party
from google import genai

load_dotenv()

# NOTE: Can be cached with lru_cache
# Gemini connection as a shared dependency
def get_gemini():
    # Initilize geni AI client to use Gemini
    client = genai.Client(api_key=os.getenv('GEMINI'))
    return client

def generate_paragraph():
    return