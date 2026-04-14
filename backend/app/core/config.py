from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and .env."""

    app_name: str = "Thesis Format Fixer Demo"
    app_env: str = "development"
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    max_upload_mb: int = 20
    storage_dir: Path = Path("storage")
    default_degree: str = "undergraduate"
    llm_provider: str = "rule_based"
    llm_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="THESIS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
