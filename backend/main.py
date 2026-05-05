from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from schemas import OptimizeCartRequest, OptimizeCartResponse
from services.query_service import optimizar_carrito
from services.gemini_service import extraer_productos_gemini, corregir_lista_texto
from database import ping_db
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="API de Optimización de Canasta Básica",
    description="Backend para calcular el costo total de la lista de compras + gasolina usando PROFECO y MongoDB.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
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
        
        resultados = await optimizar_carrito(
            latitud=request.ubicacion_usuario.latitud,
            longitud=request.ubicacion_usuario.longitud,
            productos=productos_corregidos
        )
        resultados.sort(key=lambda x: x["total_viaje"])
        
        return {
            "resultados": resultados,
            "productos_detectados": productos_corregidos # Para que el usuario vea qué entendió el sistema
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        resultados.sort(key=lambda x: x["total_viaje"])
        
        return {
            "productos_detectados": productos,
            "resultados": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando DB: {e}")

# Servir Frontend estático
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(base_dir, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
