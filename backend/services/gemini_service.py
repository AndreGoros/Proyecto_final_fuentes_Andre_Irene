import base64
import os
import json
import re
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini = genai.GenerativeModel("gemini-flash-latest")
else:
    gemini = None

# Modificamos el prompt para que CONSERVE las marcas y medidas,
# ya que ahora nuestra base de datos tiene esa capacidad gracias a la limpieza.
PROMPT_GEMINI = """
Eres un asistente experto en compras. Tu tarea es extraer productos de una lista de compras (imagen).
Analiza la imagen y devuelve SOLO un JSON con este formato exacto:
{
  "productos": ["6 litros leche lala entera", "2latas atun dolores", "1kg frijoles la costeña", "pan bimbo grande"]
}

REGLAS CRÍTICAS:
1. EXTRACCIÓN DE MARCAS: Es obligatorio incluir la marca (ej. lala, alpura, dolores, bimbo, la costeña) si es visible.
2. CANTIDADES: Si la lista indica una cantidad (ej. 6 piezas, 3 litros, 2kg), pon el número al INICIO del string (ej. "3 litros leche...").
3. DETALLES: Incluye especificaciones como "entera", "deslactosada", "en aceite", "negros", etc.
4. TODO EN MINÚSCULAS.
5. NO uses nombres genéricos si hay marcas visibles.
6. Si no hay cantidad especificada, asume 1 pero no es necesario poner el "1" al inicio a menos que sea explícito.
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

PROMPT_CORRECCION = """
Eres un experto en compras. Tu tarea es corregir y normalizar una lista de productos que puede tener errores ortográficos o términos informales.
Devuelve SOLO un JSON con este formato exacto:
{
  "productos": ["producto 1", "producto 2"]
}

REGLAS:
1. CORRIGE ERRORES: Ej: "gitomate" -> "jitomate", "leche lala 6l" -> "6 litros leche lala".
2. SEPARA PRODUCTOS: Si vienen en una sola línea separados por comas, sepáralos.
3. CONSERVA MARCAS: Si el usuario especifica marca, mantenla.
4. CANTIDADES AL INICIO: Pon el número al inicio.
5. TODO EN MINÚSCULAS.
"""

def corregir_lista_texto(texto_usuario: str) -> list[str]:
    if not gemini:
        # Si no hay API KEY, devolvemos la lista tal cual (fallo elegante)
        return [p.strip().lower() for p in texto_usuario.split(",") if p.strip()]
        
    try:
        response = gemini.generate_content(f"{PROMPT_CORRECCION}\n\nLISTA: {texto_usuario}")
        texto = response.text.strip()
        texto = re.sub(r"```json|```", "", texto).strip()
        data = json.loads(texto)
        return [p.lower().strip() for p in data.get("productos", [])]
    except Exception as e:
        print(f"ERROR en Gemini: {e}")
        # Fallback: devolver la lista original separada por comas
        return [p.strip().lower() for p in texto_usuario.split(",") if p.strip()]
