
import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from database import db
async def f():
    count = await db.precios.count_documents({})
    print(f"Total documentos: {count}")
    idxs = await db.precios.index_information()
    print(f"Indices: {idxs}")
    # Ver un ejemplo
    one = await db.precios.find_one({})
    print(f"Ejemplo: {one}")
asyncio.run(f())
