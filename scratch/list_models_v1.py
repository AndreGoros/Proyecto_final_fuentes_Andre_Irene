
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
# Forzar API version v1
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})

try:
    print("Listing models (v1)...")
    for model in client.models.list():
        if "flash" in model.name:
            print(f"Model: {model.name}")
except Exception as e:
    print(f"Error listing models (v1): {e}")
