import asyncio
from backend.services.query_service import optimizar_carrito
from dotenv import load_dotenv

load_dotenv()

async def test_missing():
    # Coordenadas de Walmart del screenshot (aprox)
    lat, lon = 19.3445, -99.1997
    productos = ["pan bimbo", "jamon de pavo", "queso manchego"]
    
    res = await optimizar_carrito(lat, lon, productos)
    
    for tienda in res:
        print(f"\nTienda: {tienda['cadena']}")
        print(f"Encontrados: {[p['producto'] for p in tienda['productos_encontrados']]}")
        print(f"Faltantes: {tienda['productos_no_encontrados']}")

if __name__ == "__main__":
    asyncio.run(test_missing())
