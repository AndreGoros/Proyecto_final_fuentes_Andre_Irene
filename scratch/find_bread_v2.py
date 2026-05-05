import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def find_bread():
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB", "precios_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database(db_name)
    collection = db.precios
    
    # Buscar productos que tengan "pan" y NO tengan "molido" ni "empanizador"
    cursor = collection.find({
        "nombre_simplificado": {
            "$regex": "pan", "$options": "i",
            "$not": {"$regex": "molido|empanizador", "$options": "i"}
        }
    }).limit(30)
    
    print("--- Otros tipos de PAN encontrados ---")
    async for doc in cursor:
        print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']} ({doc['categoria']})")

    client.close()

if __name__ == "__main__":
    asyncio.run(find_bread())
