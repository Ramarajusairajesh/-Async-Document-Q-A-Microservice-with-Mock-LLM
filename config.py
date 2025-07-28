from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/qna_db"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "qna_db"
    POSTGRES_HOST: str = "db"  # 'db' for Docker, 'localhost' for local
    POSTGRES_PORT: int = 5432
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG_MODE: bool = True
    SECRET_KEY: str = "supersecretkey"


settings = Settings()
print("Loaded Settings:")
print(f"  DATABASE_URL: {settings.DATABASE_URL}")
print(f"  SERVER_HOST: {settings.SERVER_HOST}")
print(f"  SERVER_PORT: {settings.SERVER_PORT}")
print(f"  DEBUG_MODE: {settings.DEBUG_MODE}")
