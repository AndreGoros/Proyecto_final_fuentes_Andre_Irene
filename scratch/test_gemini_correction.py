import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from backend.services.gemini_service import corregir_lista_texto

def test_correction():
    user_input = "6 litros de leche Lala, 2 latas de atun, 3 kg de gitomate, 1 kg de cebolla, huevo, 1 bolsa de arros"
    print(f"Input: {user_input}")
    
    corrected = corregir_lista_texto(user_input)
    print(f"Corrected: {corrected}")

if __name__ == "__main__":
    test_correction()
