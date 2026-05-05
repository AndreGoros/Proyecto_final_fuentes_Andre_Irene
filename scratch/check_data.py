
import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from database import db
async def f():
    doc = await db.precios.find_one({"nombre_simplificado": {"$regex": "atun"}})
    print(f"Atun doc: {doc}")
    doc2 = await db.precios.find_one({"nombre_simplificado": {"$regex": "jitomate"}})
    print(f"Jitomate doc: {doc2}")
asyncio.run(f())
