from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional, Dict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Global App Settings
    APP_NAME: str = "NLP SQL Engine"
    ENVIRONMENT: str = "development"  # Options: development, staging, production
    DEBUG: bool = ENVIRONMENT == "development"
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"

    # Api keys
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None  # Base URL for self-hosted LLMs

    # Planner LLM Settings
    PLANNER_LLM_PROVIDER: str = "local"  # Options: openai, openrouter, local, mock
    PLANNER_LLM_MODEL_NAME: str = "phi-3-mini-4k-instruct"
    PLANNER_LLM_BASE_URL: Optional[str] = None  # Base URL for self-hosted LLMs
    PLANNER_LLM_TEMPERATURE: float = 0.2
    PLANNER_LLM_API_KEY: Optional[str] = None  # For providers that need API keys

    # Smart LLM Settings
    GENERATION_LLM_PROVIDER: str = "local"  # Options: openai, openrouter, local, mock
    GENERATION_LLM_MODEL_NAME: str = "phi-3-mini-4k-instruct"
    GENERATION_LLM_BASE_URL: Optional[str] = None  # Base URL for self-hosted LLMs
    GENERATION_LLM_TEMPERATURE: float = 0.0
    GENERATION_LLM_API_KEY: Optional[str] = None  # For providers that need API keys

    # Error Correction LLM Settings
    DEBUG_LLM_PROVIDER: str = "local"  # Options: openai, openrouter, local, mock
    DEBUG_LLM_MODEL_NAME: str = "phi-3-mini-4k-instruct"
    DEBUG_LLM_BASE_URL: Optional[str] = None  # Base URL for self-hosted LLMs
    DEBUG_LLM_TEMPERATURE: float = 0.0
    DEBUG_LLM_API_KEY: Optional[str] = None  # For providers that need API keys

    @model_validator(mode="after")
    def populate_defaults(self) -> "Settings":
        default_key = self.OPENAI_API_KEY or ""
        default_url = self.LLM_BASE_URL or "http://localhost:1234/v1"

        if not self.PLANNER_LLM_API_KEY:
            self.PLANNER_LLM_API_KEY = default_key
        if not self.PLANNER_LLM_BASE_URL:
            self.PLANNER_LLM_BASE_URL = default_url

        if not self.GENERATION_LLM_API_KEY:
            self.GENERATION_LLM_API_KEY = default_key
        if not self.GENERATION_LLM_BASE_URL:
            self.GENERATION_LLM_BASE_URL = default_url

        if not self.DEBUG_LLM_API_KEY:
            self.DEBUG_LLM_API_KEY = default_key
        if not self.DEBUG_LLM_BASE_URL:
            self.DEBUG_LLM_BASE_URL = default_url

        return self

    # Embedding Settings
    EMBEDDING_PROVIDER: str = "gemini"  # Options: gemini, openai, huggingface, local, mock
    EMBEDDING_MODEL_NAME: str = "gemini-embedding-001"
    EMBEDDING_BASE_URL: Optional[str] = None  # Base URL for embedding API if needed
    EMBEDDING_API_KEY: Optional[str] = None  # For providers that need API keys

    @property
    def resolved_embedding_api_key(self) -> str:
        return self.EMBEDDING_API_KEY or self.GEMINI_API_KEY or self.OPENAI_API_KEY or ""

    # Database Settings
    DB_MANAGER: str = "default"
    DB_MANAGER_ADAPTER: str = "default"
    DB_TYPE: str = "federated"  # Options: sqlalchemy, federated, mock


    # redundant - but kept for backward compatibility
    DATABASES: Dict[str, str] = {
        "crm": "sqlite:///test_database/crm.db",
        "inventory": "sqlite:///test_database/inventory.db",
        "sales": "sqlite:///test_database/sales.db",
    }

    # The "Compiler" Engine (In-Memory DuckDB)
    FEDERATED_DB_MAIN: str = "duckdb:///:memory:"

    # Physical Layer
    FEDERATED_ATTACHMENTS: dict = {
        "crm": "sqlite:///test_database/crm.db",
        "inventory": "sqlite:///test_database/inventory.db",
        "sales": "sqlite:///test_database/sales.db",
    }

    # SEMANTIC LAYER (The Virtual Contract)
    # Virtual Tables: Map "Virtual Name" -> "Physical Path"
    VIRTUAL_SCHEMA: dict = {
        "customers": "crm.customers",
        "reviews": "crm.reviews",
        "products": "inventory.products",
        "categories": "inventory.categories",
        "suppliers": "inventory.suppliers",
        "orders": "sales.orders",
        "order_items": "sales.order_items",
        "payments": "sales.payments",
    }

    # Semantic Graph: Define Joins explicitly (since Views hide FKs)
    # Format: (Table, Column) -> (ReferencedTable, ReferencedColumn)
    VIRTUAL_RELATIONSHIPS: list = [
        # Sales -> Customers
        (("orders", "customer_id"), ("customers", "id")),
        # Sales -> Inventory
        (("order_items", "product_id"), ("products", "id")),
        (("order_items", "order_id"), ("orders", "id")),
        # Inventory Internal
        (("products", "category_id"), ("categories", "id")),
        (("products", "supplier_id"), ("suppliers", "id")),
        # CRM Internal
        (("reviews", "customer_id"), ("customers", "id")),
        (("reviews", "product_id"), ("products", "id")),
    ]

    # Vector store
    VECTOR_STORE_PROVIDER: str = "local"


settings = Settings()
