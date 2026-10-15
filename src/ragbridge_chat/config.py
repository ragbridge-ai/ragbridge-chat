"""Application settings, loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings.

    Values are read from environment variables (or a local ``.env`` file).
    See ``.env.example`` for the full list of supported variables.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = (
        "postgresql+psycopg://ragbridge_chat:ragbridge_chat@localhost:5433/ragbridge_chat"
    )
    """The gateway's own database. It holds conversations and tenant settings, never
    documents: those stay in the core's database."""


@lru_cache
def get_settings() -> Settings:
    """Return the settings, read once per process."""
    return Settings()
