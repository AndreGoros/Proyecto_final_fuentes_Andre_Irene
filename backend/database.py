import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline1234@localhost:27017/precios_db?authSource=admin")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "precios_db")

client = AsyncIOMotorClient(
    MONGO_URI,
    # Opciones recomendadas para Atlas en producción:
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    maxPoolSize=10,
)

db = client[MONGO_DB_NAME]

async def ping_db():
    """Verifica la conexión asíncrona a la base de datos."""
    try:
        await db.command("ping")
        return True
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")
        return False
