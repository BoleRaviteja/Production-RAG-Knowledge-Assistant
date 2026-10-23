from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "RAG Knowledge Assistant"
    environment: str = "local"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://rag:rag@localhost:5432/rag"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    embedding_provider: Literal["openai", "fake"] = "fake"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"

    llm_provider: Literal["anthropic", "mock"] = "mock"
    llm_model: str = "claude-sonnet-4-6"
    anthropic_api_key: str | None = None

    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5
    min_similarity: float = 0.0
    max_upload_mb: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
