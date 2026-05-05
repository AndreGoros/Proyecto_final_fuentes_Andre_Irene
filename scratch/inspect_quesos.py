import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def list_cheese_types():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline_pass@localhost:27017/profeco_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database()
    collection = db.precios
    
    # Buscar productos que contengan "queso"
    cursor = collection.find({"nombre_simplificado": {"$regex": "queso", "$options": "i"}}).limit(20)
    
    seen = set()
    print("--- Algunos quesos encontrados en la DB ---")
    async for doc in cursor:
        name = f"{doc['producto']} {doc['marca']} {doc['presentacion']}".lower()
        if name not in seen:
            print(f"- {name}")
            seen.add(name)
            
    # Buscar específicamente manchego
    print("\n--- Buscando Manchego ---")
    cursor_manchego = collection.find({"nombre_simplificado": {"$regex": "manchego", "$options": "i"}}).limit(5)
    async for doc in cursor_manchego:
         print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(list_cheese_types())
