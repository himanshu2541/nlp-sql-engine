from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Global App Settings
    APP_NAME: str = "NLP SQL Engine"
    ENVIRONMENT: str = "development"  # Options: development, staging, production
    DEBUG: bool = ENVIRONMENT == "development"
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"

    # Database Settings


    # Database connection string

settings = Settings()
