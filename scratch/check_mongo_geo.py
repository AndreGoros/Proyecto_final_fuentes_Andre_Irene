import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check():
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]
    print("Indexes in 'precios':")
    indexes = await db.precios.index_information()
    for name, info in indexes.items():
        print(f"  {name}: {info}")
    
    # Test a simple geoNear
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [-99.199, 19.344]},
                "distanceField": "dist",
                "maxDistance": 10000,
                "spherical": True
            }
        },
        {"$limit": 1}
    ]
    try:
        res = await db.precios.aggregate(pipeline).to_list(length=1)
        print(f"GeoNear test result count: {len(res)}")
    except Exception as e:
        print(f"GeoNear test failed: {e}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(check())
