from functools import lru_cache
from pathlib import Path

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    # Use the backend/.env file (absolute path) so settings load correctly
    # even when the process CWD differs (e.g. uvicorn --app-dir backend).
    model_config = SettingsConfigDict(env_file=str(_ENV_PATH), extra="ignore")

    supabase_url: str = Field(validation_alias=AliasChoices("SUPABASE_URL"))
    supabase_anon_key: str = Field(validation_alias=AliasChoices("SUPABASE_ANON_KEY"))
    supabase_service_role_key: str = Field(validation_alias=AliasChoices("SUPABASE_SERVICE_ROLE_KEY"))
    groq_api_key: str | None = Field(default=None, validation_alias=AliasChoices("GROQ_API_KEY"))
    cors_origins: list[str] = Field(default_factory=lambda: ["*"], validation_alias=AliasChoices("CORS_ORIGINS"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
