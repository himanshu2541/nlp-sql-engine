from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Global App Settings
    APP_NAME: str = "NLP SQL Engine"
    ENVIRONMENT: str = "development"  # Options: development, staging, production
    DEBUG: bool = ENVIRONMENT == "development"
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"

    # Api keys
    OPENAI_API_KEY: str = "type-your-openai-api-key-here"
    LLM_BASE_URL: Optional[str] = (
        "http://localhost:1234/v1"  # Base URL for self-hosted LLMs
    )

    # Planner LLM Settings
    PLANNER_LLM_PROVIDER: str = "local"  # Options: openai, local, mock
    PLANNER_LLM_MODEL_NAME: str = "phi-3-mini-4k-instruct"
    PLANNER_LLM_BASE_URL: Optional[str] = LLM_BASE_URL  # Base URL for self-hosted LLMs
    PLANNER_LLM_TEMPERATURE: float = 0.2
    PLANNER_LLM_API_KEY: str = OPENAI_API_KEY  # For providers that need API keys

    # Smart LLM Settings
    GENERATION_LLM_PROVIDER: str = "local"  # Options: openai, local, mock
    GENERATION_LLM_MODEL_NAME: str = "phi-3-mini-4k-instruct"
    GENERATION_LLM_BASE_URL: Optional[str] = (
        LLM_BASE_URL  # Base URL for self-hosted LLMs
    )
    GENERATION_LLM_TEMPERATURE: float = 0.0
    GENERATION_LLM_API_KEY: str = OPENAI_API_KEY  # For providers that need API keys

    # Error Correction LLM Settings
    DEBUG_LLM_PROVIDER: str = "local"  # Options: openai, local, mock
    DEBUG_LLM_MODEL_NAME: str = "phi-3-mini-4k-instruct"
    DEBUG_LLM_BASE_URL: Optional[str] = LLM_BASE_URL  # Base URL for self-hosted LLMs
    DEBUG_LLM_TEMPERATURE: float = 0.0
    DEBUG_LLM_API_KEY: str = OPENAI_API_KEY  # For providers that need API keys

    # Embedding Settings
    EMBEDDING_PROVIDER: str = "local"  # Options: openai, huggingface, local, mock
    EMBEDDING_MODEL_NAME: str = (
        "text-embedding-nomic-embed-text-v1.5"  # or text-embedding-ada-002
    )
    EMBEDDING_BASE_URL: Optional[str] = (
        "http://localhost:1234/v1"  # Base URL for embedding API if needed
    )
    EMBEDDING_API_KEY: str = "type-anything-here"  # For providers that need API keys

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
