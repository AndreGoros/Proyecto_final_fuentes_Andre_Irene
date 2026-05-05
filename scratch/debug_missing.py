import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_missing_items():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline_pass@localhost:27017/profeco_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_database()
    collection = db.precios
    
    items = ["pan bimbo", "jamon de pavo"]
    
    for t in items:
        print(f"\n--- Buscando: {t} ---")
        # Búsqueda de texto
        cursor = collection.find({"$text": {"$search": t}}).limit(5)
        async for doc in cursor:
             print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']} (Score: {doc.get('score')})")
             
        # Búsqueda de regex por si acaso
        print(f"--- Buscando {t} (Regex) ---")
        cursor_re = collection.find({"nombre_simplificado": {"$regex": t.replace(" ", ".*"), "$options": "i"}}).limit(3)
        async for doc in cursor_re:
             print(f"- {doc['producto']} {doc['marca']} {doc['presentacion']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(debug_missing_items())
