from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    backend_port: int = 8000
    frontend_port: int = 3000
    app_name: str = "PharmaShield India AI"
    api_prefix: str = "/api"

    # MongoDB
    mongo_uri: str = ""

    # PostgreSQL
    postgres_url: str = ""

    # Auth
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Default for MVP
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440 # 24 hours

    # LLM (mock for MVP)
    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "pharmashield_documents"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])


@lru_cache
def get_settings() -> Settings:
    return Settings()
