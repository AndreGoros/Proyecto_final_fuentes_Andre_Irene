import base64
import os
import json
import re
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini = None

# Modificamos el prompt para que CONSERVE las marcas y medidas,
# ya que ahora nuestra base de datos tiene esa capacidad gracias a la limpieza.
PROMPT_GEMINI = """
Eres un asistente que extrae nombres de productos de una lista de compras.
Analiza la imagen y devuelve SOLO un JSON con este formato exacto, sin texto adicional:
{
  "productos": ["leche lala deslactosada 1l", "pan bimbo blanco", "huevo san juan 18 piezas"]
}
IMPORTANTE: Los nombres deben incluir la marca, tamaño, cantidad y especificaciones tal como aparecen en la imagen. No uses nombres genéricos si en la foto hay una marca clara.
TODO EL TEXTO DEBE ESTAR EN MINÚSCULAS.
"""

def extraer_productos_gemini(imagen_bytes: bytes, mime_type: str) -> list[str]:
    if not gemini:
        raise ValueError("GEMINI_API_KEY no configurada. Añádela en el archivo .env o en el entorno.")
        
    imagen_b64 = base64.b64encode(imagen_bytes).decode()
    response = gemini.generate_content([
        {"mime_type": mime_type, "data": imagen_b64},
        PROMPT_GEMINI,
    ])
    
    texto = response.text.strip()
    texto = re.sub(r"```json|```", "", texto).strip()
    data = json.loads(texto)
    return [p.lower().strip() for p in data.get("productos", [])]
