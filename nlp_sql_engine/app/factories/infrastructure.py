import json
from typing import Any
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.app.registry import ProviderRegistry
from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.core.interfaces.manager import IDatabaseManager


class InfrastructureFactory:
    """
    Factory class to instantiate infrastructure providers based on configuration.
    """

    @staticmethod
    def create_llm(
        provider_name: str,
        model_name: str,
        api_key: str,
        temperature: float,
        **kwargs: Any,
    ) -> ILLMProvider:
        llm_class = ProviderRegistry.get_llm_class(provider_name)
        return llm_class(
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            **kwargs,
        )

    @staticmethod
    def create_db(settings: Settings) -> IDatabaseConnector:
        # Example: DB_TYPE="sqlite", DB_CONNECTION_STRING="file.db"
        db_type = getattr(settings, "DB_TYPE", "sqlite").lower()
        conn_string = getattr(settings, "DB_CONNECTION_STRING", ":memory:")

        db_class = ProviderRegistry.get_db_class(db_type)

        # Depending on IDatabaseConnector __init__, pass the string
        return db_class(conn_string)

    @staticmethod
    def create_embedding(settings: Settings) -> IEmbeddingProvider:
        provider_name = getattr(settings, "EMBEDDING_PROVIDER", "local").lower()
        embed_class = ProviderRegistry.get_embedding_class(provider_name)

        return embed_class(settings)

    @staticmethod
    def create_db_manager(settings: Settings) -> IDatabaseManager:
        manager_type = getattr(settings, "DB_MANAGER_TYPE", "default").lower()
        manager_class = ProviderRegistry.get_manager_class(manager_type)

        # Instantiation
        manager = manager_class()

        databases = {}

        if hasattr(settings, "DATABASES") and settings.DATABASES:
            if isinstance(settings.DATABASES, str):
                databases = json.loads(settings.DATABASES)
            else:
                databases = settings.DATABASES
        else:
            default_conn = getattr(settings, "DB_CONNECTION_STRING", ":memory:")
            databases = {"default": default_conn}

        db_type = getattr(settings, "DB_TYPE", "sqlite").lower()
        db_class = ProviderRegistry.get_db_class(db_type)

        if hasattr(manager, "register_adapter"):
            for name, conn_str in databases.items():
                adapter = db_class(conn_str)
                manager.register_adapter(name, adapter)

        return manager
