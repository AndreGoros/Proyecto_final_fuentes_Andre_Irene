
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

try:
    m = client.models.get(model="gemini-flash-latest")
    print(f"Model flash-latest found: {m.name}")
except Exception as e:
    print(f"Model flash-latest NOT found: {e}")
