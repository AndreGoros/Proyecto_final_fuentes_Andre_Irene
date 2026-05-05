import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def test():
    client = AsyncIOMotorClient("mongodb://pipeline_user:pipeline1234@localhost:27017/precios_db?authSource=admin")
    db = client.precios_db
    docs = await db.precios.find().limit(5).to_list(5)
    print(json.dumps(docs, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(test())
