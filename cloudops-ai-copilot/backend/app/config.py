"""
CloudOps AI Copilot — Application Configuration

Loads settings from environment variables using pydantic-settings.
All config is centralized here to avoid scattered env lookups.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ----- Application -----
    app_name: str = "CloudOps AI Copilot"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True

    # ----- Database -----
    database_url: str = (
        "postgresql+asyncpg://copilot:copilot_secret@localhost:5432/cloudops_copilot"
    )

    # ----- Auth / JWT -----
    secret_key: str = "change-me-to-a-random-64-char-hex-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # ----- AI Providers -----
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    default_ai_provider: str = "gemini"

    # ----- CORS -----
    cors_origins: str = '["http://localhost:3000","http://127.0.0.1:3000"]'

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from JSON string to list."""
        try:
            return json.loads(self.cors_origins)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:3000"]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton instance
settings = Settings()
