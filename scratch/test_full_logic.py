
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Mocking database before imports
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

import database
database.db = MagicMock()
database.db.precios = MagicMock()

from services.query_service import optimizar_carrito

async def run_test():
    print("Simulando búsqueda con marcas reales de los CSV...")
    print("-" * 50)
    
    # Mocking sucursales (Paso 1)
    mock_sucursales = [
        {
            "_id": [-102.292976, 21.832072],
            "cadena": "Walmart",
            "sucursal": "WALMART SUPERCENTER AGUASCALIENTES",
            "direccion": "Av. Mahatma Gandhi S/n",
            "distancia_mts": 2000
        }
    ]
    
    cursor_geo = AsyncMock()
    cursor_geo.to_list.return_value = mock_sucursales
    database.db.precios.aggregate.return_value = cursor_geo
    
    # Mocking find_one (Paso 3) para diferentes productos
    async def mock_find_one(query, sort=None):
        regex = query["nombre_simplificado"]["$regex"]
        print(f"🔍 Buscando en DB con regex: {regex}")
        
        if "aguascalientes" in regex:
            return {
                "producto": "LECHE ULTRAPASTEURIZADA ENTERA AGUASCALIENTES 1L",
                "precio": 23.50
            }
        if "marinela" in regex and "chocoroles" in regex:
            return {
                "producto": "PASTELILLOS CHOCOROLES MARINELA 100G",
                "precio": 17.00
            }
        if "huevo" in regex:
            return {
                "producto": "HUEVO BLANCO EL CALVARIO 18 PIEZAS",
                "precio": 45.00
            }
        return None

    database.db.precios.find_one = mock_find_one
    
    # Caso 1: Con marcas y cantidades
    productos_test = [
        "6 litros leche aguascalientes",
        "2 chocoroles marinela",
        "huevo" # Genérico, debe traer el primero (mockeado como El Calvario)
    ]
    
    print(f"Lista de prueba: {productos_test}")
    resultados = await optimizar_carrito(21.83, -102.29, productos_test)
    
    for res in resultados:
        print(f"\n🏪 Sucursal: {res['cadena']} ({res['sucursal']})")
        print(f"   Distancia: {res['distancia_km']} km | Gasolina: ${res['costo_gasolina']}")
        print(f"   --- Productos Encontrados ---")
        for p in res['productos_encontrados']:
            print(f"   ✅ {p['cantidad']}x {p['producto']}")
            print(f"      Unit: ${p['precio_unitario']} | Total: ${p['precio_total']}")
        print(f"   ---")
        print(f"   💰 SUBTOTAL: ${res['subtotal_productos']}")
        print(f"   🚀 TOTAL (inc. gas): ${res['total_viaje']}")

if __name__ == "__main__":
    asyncio.run(run_test())
