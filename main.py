import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, db_instance
from app.routes.auth_routes import router as auth_router
from app.routes.question_routes import router as question_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB on startup
    logger.info("Initializing application and connecting to MongoDB...")
    await connect_to_mongo()
    yield
    # Clean up MongoDB connection on shutdown
    logger.info("Shutting down application...")
    await close_mongo_connection()

app = FastAPI(
    title="FastAPI MCQ Question API Server",
    description=(
        "Production-ready FastAPI server with MongoDB Atlas integration, "
        "JWT authentication session handling, and MCQ Question upload and retrieval routes."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Enable CORS for all origins so any frontend or API client can consume endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router)
app.include_router(question_router)

@app.get("/", tags=["Health"])
async def root():
    mongo_status = "connected" if db_instance.client is not None else "connecting/disconnected"
    return {
        "status": "online",
        "service": "FastAPI MCQ Question Server",
        "database": {
            "type": "MongoDB Atlas",
            "status": mongo_status,
            "database_name": settings.database_name
        },
        "endpoints": {
            "docs_swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "auth": {
                "signup": "POST /auth/signup",
                "login": "POST /auth/login",
                "me": "GET /auth/me"
            },
            "questions": {
                "upload": "POST /questions (requires Bearer JWT)",
                "list": "GET /questions",
                "get_by_id": "GET /questions/{question_id}"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
