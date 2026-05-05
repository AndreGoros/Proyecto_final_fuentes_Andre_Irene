import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline1234@localhost:27017/precios_db?authSource=admin")
MONGO_DB = os.getenv("MONGO_DB", "precios_db")

async def check_items():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    
    queries = [
        {"name": "Leche Lala", "filter": {"nombre_simplificado": {"$regex": "leche.*lala", "$options": "i"}}},
        {"name": "Chocorroles", "filter": {"nombre_simplificado": {"$regex": "chocorol", "$options": "i"}}},
        {"name": "Papa", "filter": {"nombre_simplificado": {"$regex": "papa", "$options": "i"}}},
        {"name": "Atun", "filter": {"nombre_simplificado": {"$regex": "atun", "$options": "i"}}},
    ]
    
    for q in queries:
        count = await db.precios.count_documents(q["filter"])
        print(f"Query: {q['name']} - Count: {count}")
        if count > 0:
            sample = await db.precios.find_one(q["filter"])
            print(f"  Sample: {sample.get('producto')} | Simplificado: {sample.get('nombre_simplificado')}")
        else:
            # Try a broader search
            broad_filter = {"producto": {"$regex": q['name'].split()[0], "$options": "i"}}
            broad_count = await db.precios.count_documents(broad_filter)
            print(f"  Broad search '{q['name'].split()[0]}' Count: {broad_count}")
            if broad_count > 0:
                sample = await db.precios.find_one(broad_filter)
                print(f"    Broad Sample: {sample.get('producto')} | Simplificado: {sample.get('nombre_simplificado')}")

    client.close()

if __name__ == "__main__":
    asyncio.run(check_items())
