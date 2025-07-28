# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """

    # Model configuration: allows loading settings from a .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/qna_db"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "qna_db"
    POSTGRES_HOST: str = "db"  # 'db' for Docker, 'localhost' for local
    POSTGRES_PORT: int = 5432

    # Server settings
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # Debug mode for development (enables auto-reload)
    DEBUG_MODE: bool = True

    # Secret key for any future authentication/security needs (example)
    SECRET_KEY: str = "supersecretkey"


# Create a settings instance to be used throughout the application
settings = Settings()

# Print loaded settings (for debugging purposes)
print("Loaded Settings:")
print(f"  DATABASE_URL: {settings.DATABASE_URL}")
print(f"  SERVER_HOST: {settings.SERVER_HOST}")
print(f"  SERVER_PORT: {settings.SERVER_PORT}")
print(f"  DEBUG_MODE: {settings.DEBUG_MODE}")
