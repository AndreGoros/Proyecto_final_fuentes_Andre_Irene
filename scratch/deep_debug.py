import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def deep_debug():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline_pass@localhost:27017/profeco_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database()
    collection = db.precios
    
    print("--- Buscando productos que tengan 'Bimbo' ---")
    cursor = collection.find({"nombre_simplificado": {"$regex": "Bimbo", "$options": "i"}}).limit(10)
    async for doc in cursor:
        print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']}")

    print("\n--- Buscando productos que tengan 'Jamon' ---")
    cursor = collection.find({"nombre_simplificado": {"$regex": "Jamon", "$options": "i"}}).limit(10)
    async for doc in cursor:
        print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(deep_debug())
