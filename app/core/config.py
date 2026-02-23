from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "BazaarMind API"
    ENV: Literal["dev", "test", "prod"] = "dev"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    POSTGRES_DSN: str = "postgresql+asyncpg://app:app_password@postgres:5432/bazaarmind"
    REDIS_DSN: str = "redis://redis:6379/0"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_REUSE_GRACE_SECONDS: int = 3

    CORS_ORIGINS: list[str] = Field(default_factory=list)
    RATE_LIMIT_DEFAULT: str = "120/minute"
    PREDICTION_CACHE_TTL_SECONDS: int = 900

    MODEL_REGISTRY_PATH: str = "/app/model_registry"
    GUNICORN_WORKERS: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
