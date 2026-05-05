import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline1234@localhost:27017/precios_db?authSource=admin")
MONGO_DB = os.getenv("MONGO_DB", "precios_db")

async def inspect_items():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    
    addr = "Perpetua 35"
    print(f"--- Buscando en la sucursal {addr} ---")
    
    for term in ["atun", "arroz", "huevo"]:
        print(f"\nResultados para '{term}':")
        cursor = db.precios.find({
            "direccion": {"$regex": addr, "$options": "i"},
            "nombre_simplificado": {"$regex": term, "$options": "i"}
        }).sort("precio", 1)
        async for item in cursor:
            print(f"  Price: ${item['precio']} | Prod: {item['producto']} | Simple: {item['nombre_simplificado']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_items())
