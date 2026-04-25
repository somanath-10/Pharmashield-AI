from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    backend_port: int = 8000
    frontend_port: int = 3000
    app_name: str = "PharmaShield AI"
    api_prefix: str = "/api"
    database_url: str = "sqlite+pysqlite:///./pharmashield.db"
    qdrant_url: str = "http://localhost:6333"
    redis_url: str = "redis://localhost:6379/0"
    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_base_url: str | None = None
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    enable_live_public_apis: bool = True
    enable_synthetic_data: bool = True
    enable_india_mode: bool = True
    max_retrieved_chunks: int = 20
    max_reranked_chunks: int = 8
    upload_dir: str = "storage/uploads"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
