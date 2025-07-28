# main.py
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
import asyncio
import logging

# Import database and models for startup/shutdown events
from database import init_db, close_db

# Import routers directly from their module paths to avoid circular imports
from routers.document_router import router as document_router_instance
from routers.question_router import router as question_router_instance
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup and shutdown events.
    Initializes the database on startup and closes connections on shutdown.
    """
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
    """
    Endpoint to check the health and uptime of the service.
    """
    logger.info("Health check requested.")
    return {"status": "ok", "message": "Service is running smoothly!"}


if __name__ == "__main__":
    # This block allows you to run the FastAPI application directly
    # by executing this Python file.
    # The 'app' refers to the FastAPI instance created above.
    # The 'host' and 'port' are configured from settings.
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
