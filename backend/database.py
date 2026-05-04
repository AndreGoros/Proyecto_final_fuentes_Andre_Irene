import os
from motor.motor_asyncio import AsyncIOMotorClient

# Por defecto asume que MongoDB corre en localhost con el usuario creado en 01_init.js
MONGO_URI = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline1234@localhost:27017/precios_db?authSource=admin")

client = AsyncIOMotorClient(MONGO_URI)
db = client.precios_db

async def ping_db():
    """Verifica la conexión asíncrona a la base de datos."""
    try:
        await db.command("ping")
        return True
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")
        return False
