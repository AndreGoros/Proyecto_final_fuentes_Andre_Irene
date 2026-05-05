
import asyncio
import sys
import os

# Añadir el directorio backend al path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import db, ping_db
from services.query_service import optimizar_carrito

async def test_real():
    print("Conectando a MongoDB...")
    connected = await ping_db()
    if not connected:
        print("❌ No se pudo conectar a MongoDB. Asegúrate de que Docker esté corriendo.")
        return

    # Coordenadas exactas de Chedraui Aguascalientes (del DB check)
    lat, lon = 21.854349, -102.294259
    
    productos_test = [
        "2 atun",
        "3 kg jitomate",
        "1 kg cebolla",
        "leche lala"
    ]
    
    print(f"Buscando: {productos_test}")
    print("-" * 50)
    
    try:
        resultados = await optimizar_carrito(lat, lon, productos_test)
        
        if not resultados:
            print("⚠️ No se encontraron resultados. ¿Cargaste los datos geoespaciales correctamente?")
            return

        # Mostrar el mejor resultado
        mejor = resultados[0]
        print(f"🏆 MEJOR OPCIÓN: {mejor['cadena']} ({mejor['sucursal']})")
        print(f"📍 Dirección: {mejor['direccion']}")
        print(f"💰 TOTAL: ${mejor['total_viaje']} (Carro: ${mejor['subtotal_productos']} + Gas: ${mejor['costo_gasolina']})")
        print("\nDetalle:")
        for p in mejor['productos_encontrados']:
            print(f"  ✅ {p['cantidad']}x {p['producto']} -> ${p['precio_total']} (${p['precio_unitario']} c/u)")
        
        if mejor['productos_no_encontrados']:
            print(f"\n❌ No encontrados: {mejor['productos_no_encontrados']}")

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    asyncio.run(test_real())
