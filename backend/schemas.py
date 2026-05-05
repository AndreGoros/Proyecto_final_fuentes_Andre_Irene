from pydantic import BaseModel
from typing import List

class Ubicacion(BaseModel):
    latitud: float
    longitud: float

class OptimizeCartRequest(BaseModel):
    ubicacion_usuario: Ubicacion
    productos: List[str]

class ProductItem(BaseModel):
    producto: str
    precio_unitario: float
    cantidad: int
    precio_total: float
    distancia_km: float

class StoreResult(BaseModel):
    cadena: str
    sucursal: str
    direccion: str
    distancia_km: float
    productos_encontrados: List[ProductItem]
    productos_no_encontrados: List[str]
    subtotal_productos: float
    costo_gasolina: float
    total_viaje: float

class OptimizeCartResponse(BaseModel):
    resultados: List[StoreResult]
