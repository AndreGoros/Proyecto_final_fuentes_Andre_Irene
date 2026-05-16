from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from schemas import OptimizeCartRequest, OptimizeCartResponse
from services.query_service import optimizar_carrito
from services.gemini_service import extraer_productos_gemini, corregir_lista_texto
from database import ping_db
import os
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="API de Optimización de Canasta Básica",
    description="Backend para calcular el costo total de la lista de compras + gasolina usando PROFECO y MongoDB.",
    version="0.1.0",
)

allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")

if allowed_origins_str == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    db_ok = await ping_db()
    return {"status": "ok", "mongodb_connected": db_ok}

@app.post("/api/v1/optimizar-carrito", response_model=OptimizeCartResponse)
async def endpoint_optimizar_carrito(request: OptimizeCartRequest):
    """Ruta para cuando la lista ya es texto."""
    try:
        # Usamos Gemini para normalizar y corregir la lista (typos, marcas, etc)
        texto_unificado = ", ".join(request.productos)
        productos_corregidos = corregir_lista_texto(texto_unificado)
        print(f"DEBUG: Productos corregidos por Gemini: {productos_corregidos}")
        
        resultados = await optimizar_carrito(
            latitud=request.ubicacion_usuario.latitud,
            longitud=request.ubicacion_usuario.longitud,
            productos=productos_corregidos
        )
        # Categorizar resultados
        completos = [r for r in resultados if not r["productos_no_encontrados"]]
        incompletos = [r for r in resultados if r["productos_no_encontrados"]]
        
        return {
            "mejores_completos": completos,
            "mejores_incompletos": incompletos,
            "productos_detectados": productos_corregidos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/extraer-texto-foto")
async def api_extraer_texto_foto(foto: UploadFile = File(...)):
    """Solo extrae los productos de la foto para que el usuario los revise."""
    contenido = await foto.read()
    mime_type = foto.content_type or "image/jpeg"
    try:
        productos = extraer_productos_gemini(contenido, mime_type)
        return {"productos": productos}
    except Exception as e:
        print(f"DEBUG: Error capturado en main.py: {e}")
        raise HTTPException(status_code=422, detail=f"Error en Gemini: {str(e)}")

@app.post("/api/v1/analizar-foto")
async def analizar_foto(
    foto: UploadFile = File(..., description="Foto de la lista de compras"),
    latitud: float = Form(..., description="Latitud del usuario"),
    longitud: float = Form(..., description="Longitud del usuario"),
):
    """
    Ruta Integrada:
    1. Recibe foto y coordenadas.
    2. Gemini extrae productos manteniendo la marca.
    3. Mongo hace búsquedas geoespaciales y calcula costos totales.
    """
    contenido = await foto.read()
    mime_type = foto.content_type or "image/jpeg"
    
    try:
        productos = extraer_productos_gemini(contenido, mime_type)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error con Gemini: {e}")
        
    if not productos:
        raise HTTPException(status_code=422, detail="No se detectaron productos en la imagen.")
        
    try:
        resultados = await optimizar_carrito(
            latitud=latitud,
            longitud=longitud,
            productos=productos
        )
        # Categorizar resultados
        completos = [r for r in resultados if not r["productos_no_encontrados"]]
        incompletos = [r for r in resultados if r["productos_no_encontrados"]]
        
        return {
            "mejores_completos": completos,
            "mejores_incompletos": incompletos,
            "productos_detectados": productos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando DB: {e}")

# Servir Frontend estático
# Intentar primero la ruta de Docker (donde frontend está al lado de main.py)
frontend_dir_docker = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
# Intentar la ruta local (donde frontend está un nivel arriba)
frontend_dir_local = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(frontend_dir_docker):
    app.mount("/", StaticFiles(directory=frontend_dir_docker, html=True), name="frontend")
elif os.path.exists(frontend_dir_local):
    app.mount("/", StaticFiles(directory=frontend_dir_local, html=True), name="frontend")
else:
    print("WARNING: No se encontró el directorio frontend ni en local ni en docker path")
