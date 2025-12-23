from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Global App Settings
    APP_NAME: str = "NLP SQL Engine"
    ENVIRONMENT: str = "development"  # Options: development, staging, production
    DEBUG: bool = ENVIRONMENT == "development"
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"

    # LLM Settings
    LLM_PROVIDER: str = "local"  # Options: openai, local, mock
    LLM_MODEL_NAME: str = "phi-3-mini-4k-instruct"  # e.g., gpt-3.5-turbo, phi3-mini
    LLM_BASE_URL: Optional[str] = "http://localhost:1234/v1"  # Base URL for self-hosted LLMs
    LLM_TEMPERATURE: float = 0.0 # SQL should be deterministic 
    LLM_API_KEY: Optional[str] = None  # For providers that need API keys
    
    # Embedding Settings
    EMBEDDING_PROVIDER: str = "local"  # Options: openai, huggingface, local, mock
    EMBEDDING_MODEL_NAME: str = "text-embedding-nomic-embed-text-v1.5"  # or text-embedding-ada-002
    EMBEDDING_BASE_URL: Optional[str] = "http://localhost:1234/v1"  # Base URL for embedding API if needed
    EMBEDDING_API_KEY: Optional[str] = None  # For providers that need API keys

    # Database Settings
    DB_TYPE: str = "sqlite"  # Options: sqlite, postgresql, mysql, etc.
    DB_CONNECTION_STRING: str = ":memory:"  # e.g., sqlite:///./test.db or postgresql://user:pass@localhost/dbname
    
settings = Settings()
