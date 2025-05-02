from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@postgres:5432/enterprise_manager",
    )

    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your_jwt_secret_key")
    JWT_REFRESH_SECRET: str = os.getenv(
        "JWT_REFRESH_SECRET", "your_jwt_refresh_secret_key"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000",
    ]

    # Security settings
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"

    class Config:
        env_file = ".env"


settings = Settings()
