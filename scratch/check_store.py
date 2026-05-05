
import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from database import db
async def f():
    docs = await db.precios.find({'location.coordinates': [-102.294259, 21.854349]}).to_list(500)
    print(f"Productos en esta tienda: {len(docs)}")
    productos = sorted(list(set([d['producto'] for d in docs])))
    for doc in docs:
        if "cebolla" in doc['nombre_simplificado']:
            print(f" - Original: {doc['producto']} | Simplificado: {doc['nombre_simplificado']}")
asyncio.run(f())
