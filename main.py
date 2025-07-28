from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
import asyncio
import logging

from database import init_db, close_db

from routers.document_router import router as document_router_instance
from routers.question_router import router as question_router_instance
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing database...")
    await init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Application shutdown: Closing database connections...")
    await close_db()
    logger.info("Database connections closed.")


app = FastAPI(
    title="AI Document Q&A Microservice",
    description="Backend service for an AI document Q&A app, featuring document upload, question submission, and simulated LLM answers.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers for different API functionalities
# Use the imported router instances directly
app.include_router(document_router_instance, prefix="/documents", tags=["Documents"])
app.include_router(question_router_instance, prefix="/questions", tags=["Questions"])


@app.get("/health", summary="Health Check", response_model=dict)
async def health_check():
    logger.info("Health check requested.")
    return {"status": "ok", "message": "Service is running smoothly!"}


if __name__ == "__main__":
    app.include_router(
        question_router_instance, prefix="/questions", tags=["Questions"]
    )
    logger.info(
        f"Starting Uvicorn server on {settings.SERVER_HOST}:{settings.SERVER_PORT}"
    )
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG_MODE,  # Reload for development if DEBUG_MODE is True
    )
