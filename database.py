from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)
Base = declarative_base()
engine = None
AsyncSessionLocal = None


async def init_db():
    global engine, AsyncSessionLocal
    try:
        engine = create_async_engine(
            settings.DATABASE_URL, echo=True
        )  # echo=True for SQL logging
        # Create database tables defined by Base metadata
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # Create an async session maker
        AsyncSessionLocal = async_sessionmaker(
            autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
        )
        logger.info("Database engine and session initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Re-raise the exception to prevent the application from starting if DB init fails
        raise


async def close_db():
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database engine disposed.")


async def get_db_session():
    if AsyncSessionLocal is None:
        logger.error("AsyncSessionLocal is not initialized. Call init_db() first.")
        raise RuntimeError("Database session not initialized.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_session_for_background_task():
    if AsyncSessionLocal is None:
        logger.error("AsyncSessionLocal is not initialized. Call init_db() first.")
        raise RuntimeError("Database session not initialized.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
