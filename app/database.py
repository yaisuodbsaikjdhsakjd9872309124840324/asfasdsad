from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger("uvicorn.error")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB Atlas...")
    try:
        db_instance.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000
        )
        db_instance.db = db_instance.client[settings.database_name]
        # Ping the server to verify credentials
        await db_instance.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas!")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    return db_instance.db

def get_users_collection():
    if db_instance.db is None:
        db_instance.client = AsyncIOMotorClient(settings.mongodb_uri)
        db_instance.db = db_instance.client[settings.database_name]
    return db_instance.db["users"]

def get_questions_collection():
    if db_instance.db is None:
        db_instance.client = AsyncIOMotorClient(settings.mongodb_uri)
        db_instance.db = db_instance.client[settings.database_name]
    return db_instance.db["questions"]
