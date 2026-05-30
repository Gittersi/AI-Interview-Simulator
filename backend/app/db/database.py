from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(settings.DATABASE_URL)
        db = client.ai_interview
        # Test connection
        await client.admin.command('ping')
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def disconnect_from_mongo():
    global client
    if client:
        client.close()
        logger.info("MongoDB disconnected")

def get_db() -> AsyncIOMotorDatabase:
    return db
