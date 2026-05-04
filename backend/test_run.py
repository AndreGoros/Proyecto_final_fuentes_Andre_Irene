import asyncio
from services.query_service import optimizar_carrito

async def main():
    # Coordenadas encontradas en Chiapas
    latitud = 16.755374
    longitud = -93.149762
    productos = ['leche', 'aceite']
    
    print(f'Buscando {productos} cerca de lat:{latitud}, lon:{longitud}...')
    resultados = await optimizar_carrito(latitud, longitud, productos)
    
    if not resultados:
        print('No se encontró nada.')
        return
        
    for res in resultados[:3]: # Mostrar top 3
        print(f'\n�� Tienda: {res["cadena"]} ({res["sucursal"]})')
        print(f'📍 Distancia: {res["distancia_km"]} km')
        print('Productos encontrados:')
        for p in res['productos_encontrados']:
            print(f'  - {p["producto"]}: ${p["precio"]}')
        print(f'💰 Subtotal Productos: ${res["subtotal_productos"]}')
        print(f'⛽ Costo Gasolina: ${res["costo_gasolina"]}')
        print(f'🚀 TOTAL DEL VIAJE: ${res["total_viaje"]}')

asyncio.run(main())
