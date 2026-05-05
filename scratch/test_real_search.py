import asyncio
import os
import re
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline1234@localhost:27017/precios_db?authSource=admin")
MONGO_DB = os.getenv("MONGO_DB", "precios_db")

def get_regex(word):
    f = word.lower()
    f = f.replace("b", "B").replace("v", "B")
    f = f.replace("g", "G").replace("j", "G")
    f = f.replace("s", "S").replace("z", "S").replace("c", "S")
    f = f.replace("B", "[bv]").replace("G", "[gj]").replace("S", "[szc]")
    f = f.replace("rr", "r").replace("r", "r+")
    if not f.startswith("h"): f = "h?" + f
    return f

async def test_real_search():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    
    items = ["leche lala", "atun", "jitomate", "cebolla", "huevo", "arroz"]
    
    for item in items:
        regex_part = get_regex(item)
        full_regex = f"(?!.*harina)(?!.*bebida)(?!.*polvo)(?!.*galletas)(?=.*{regex_part}).*"
        print(f"Searching for: {item} | Regex: {full_regex}")
        
        count = await db.precios.count_documents({"nombre_simplificado": {"$regex": full_regex, "$options": "i"}})
        print(f"  Count: {count}")
        if count > 0:
            sample = await db.precios.find_one({"nombre_simplificado": {"$regex": full_regex, "$options": "i"}})
            print(f"  Sample: {sample['nombre_simplificado']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(test_real_search())
