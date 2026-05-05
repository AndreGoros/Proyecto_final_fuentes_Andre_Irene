import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_final_cheeses():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline_pass@localhost:27017/profeco_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database()
    collection = db.precios
    
    types = ["mozzarella", "queso americano"]
    
    for t in types:
        print(f"\n--- Buscando: {t} ---")
        cursor = collection.find({"nombre_simplificado": {"$regex": t, "$options": "i"}}).limit(3)
        async for doc in cursor:
             print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(check_final_cheeses())
