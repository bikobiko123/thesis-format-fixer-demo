from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and .env."""

    app_name: str = "Thesis Format Fixer Demo"
    app_env: str = "development"
    storage_dir: Path = Path("storage")
    docx_engine: str = "openxml"
    structure_recognizer: str = "heuristic"
    llm_provider: str = "rule_based"
    llm_api_key: str | None = None
    llm_endpoint: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: int = 20
    llm_audit_log_path: Path = Path("storage/llm_structure_audit.jsonl")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="THESIS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
