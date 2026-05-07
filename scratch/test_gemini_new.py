
import os
import sys
# Añadir el directorio backend al path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv
load_dotenv()

from services.gemini_service import corregir_lista_texto

def test_gemini():
    print("Probando conexión con Gemini Flash Latest...")
    lista_sucia = "gitomate, leche lala 6l, huevo"
    try:
        resultado = corregir_lista_texto(lista_sucia)
        print(f"✅ Respuesta exitosa: {resultado}")
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")

if __name__ == "__main__":
    test_gemini()
