import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    mongodb_uri: str = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://b648265846185626_db_user:QVUh3eOc2E1n4Irc@cluster0.un50rvr.mongodb.net/"
    )
    database_name: str = os.getenv("DATABASE_NAME", "mcq_database")
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "fastapi_jwt_super_secret_mcq_token_key_2026_production"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
