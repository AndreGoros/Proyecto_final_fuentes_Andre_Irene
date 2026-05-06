import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def inspect_miel_pina():
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB", "precios_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database(db_name)
    collection = db.precios
    
    items = ["miel", "piña", "pi¥a"]
    
    for t in items:
        print(f"\n--- Buscando: {t} ---")
        cursor = collection.find({"nombre_simplificado": {"$regex": t, "$options": "i"}}).limit(5)
        async for doc in cursor:
             print(f"- Original: {doc['producto']} | Simplificado: {doc['nombre_simplificado']} | Marca: {doc['marca']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_miel_pina())
