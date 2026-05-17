
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    print("API KEY not found")
    exit()

client = genai.Client(api_key=api_key)

try:
    print("Listing models...")
    for model in client.models.list():
        print(f"Model: {model.name} | Version: {model.base_model_id if hasattr(model, 'base_model_id') else 'N/A'}")
except Exception as e:
    print(f"Error listing models: {e}")
