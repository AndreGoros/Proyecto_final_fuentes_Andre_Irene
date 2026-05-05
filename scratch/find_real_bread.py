import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def find_real_bread():
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB", "precios_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database(db_name)
    collection = db.precios
    
    # Buscar "Bimbo" que no sea empanizador
    cursor = collection.find({
        "nombre_simplificado": {
            "$regex": "bimbo", "$options": "i",
            "$not": {"$regex": "empanizador", "$options": "i"}
        }
    }).limit(10)
    
    print("--- Productos BIMBO (no empanizadores) ---")
    async for doc in cursor:
        print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']} ({doc['categoria']})")

    # Buscar "Pan" en categorías de comida
    print("\n--- Productos con 'PAN' en Panadería ---")
    cursor = collection.find({
        "categoria": {"$regex": "pan", "$options": "i"},
        "nombre_simplificado": {"$regex": "pan", "$options": "i"}
    }).limit(10)
    async for doc in cursor:
        print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(find_real_bread())
