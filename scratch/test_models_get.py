
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

try:
    m = client.models.get(model="gemini-1.5-flash")
    print(f"Model 1.5 found: {m.name}")
except Exception as e:
    print(f"Model 1.5 NOT found: {e}")

try:
    m = client.models.get(model="gemini-2.0-flash")
    print(f"Model 2.0 found: {m.name}")
except Exception as e:
    print(f"Model 2.0 NOT found: {e}")
