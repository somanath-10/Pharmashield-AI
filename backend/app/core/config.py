from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    backend_port: int = 8000
    frontend_port: int = 3000
    app_name: str = "PharmaShield India AI"
    api_prefix: str = "/api"

    # MongoDB
    database_url: str = "mongodb://localhost:27017/pharmashield_india"

    # LLM (mock for MVP)
    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])


@lru_cache
def get_settings() -> Settings:
    return Settings()
