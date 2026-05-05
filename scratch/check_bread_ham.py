import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "profeco_db")

async def check_items():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    
    queries = [
        {"name": "Pan Bimbo", "filter": {"nombre_simplificado": {"$regex": "pan.*bimbo", "$options": "i"}}},
        {"name": "Jamon Pavo", "filter": {"nombre_simplificado": {"$regex": "jamon.*pavo", "$options": "i"}}},
        {"name": "Pechuga Pavo", "filter": {"nombre_simplificado": {"$regex": "pechuga.*pavo", "$options": "i"}}},
        {"name": "Pan Blanco", "filter": {"nombre_simplificado": {"$regex": "pan.*blanco", "$options": "i"}}},
    ]
    
    for q in queries:
        count = await db.precios.count_documents(q["filter"])
        print(f"Query: {q['name']} - Count: {count}")
        if count > 0:
            sample = await db.precios.find_one(q["filter"])
            print(f"  Sample: {sample.get('producto')} | Simplificado: {sample.get('nombre_simplificado')}")

    client.close()

if __name__ == "__main__":
    asyncio.run(check_items())
