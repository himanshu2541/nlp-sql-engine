import json
from typing import Any, cast
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.app.registry import ProviderRegistry
from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.core.interfaces.manager import IDatabaseManager
from nlp_sql_engine.core.interfaces.vector_store import IVectorStore


import logging

logger = logging.getLogger(__name__)


class InfrastructureFactory:
    """
    Factory class to instantiate infrastructure providers based on configuration.
    """

    @staticmethod
    def create_llm(
        provider: str,
        model_name: str,
        api_key: str,
        temperature: float,
        **kwargs: Any,
    ) -> ILLMProvider:
        llm_class = ProviderRegistry.get_llm_class(provider)
        return llm_class(
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            **kwargs,
        )

    @staticmethod
    def create_embedding(
        provider: str, model_name: str, api_key: str, **kwargs: Any
    ) -> IEmbeddingProvider:
        embed_class = ProviderRegistry.get_embedding_class(provider)
        return embed_class(model_name=model_name, api_key=api_key, **kwargs)

    @staticmethod
    def create_vector_store(
        provider: str, embedder: IEmbeddingProvider, **kwargs
    ) -> IVectorStore:
        store_cls = ProviderRegistry.get_vector_store_class(provider)
        return store_cls(embedder=embedder)

    @staticmethod
    def create_db_manager(
        db_manager: str, db_type: str, settings: Settings, **kwargs
    ) -> IDatabaseManager:
        manager_class = ProviderRegistry.get_manager_class(db_manager)
        manager = manager_class()

        adapter_class = ProviderRegistry.get_db_class(db_type)

        if hasattr(adapter_class, "create"):
            adapter = cast(Any, adapter_class).create(settings)
            manager.register_adapter(settings.DB_MANAGER_ADAPTER, adapter)

        else:
            print(
                f"Adapter '{db_type}' does not support auto-configuration. Using legacy loader."
            )

            databases = {}
            if hasattr(settings, "DATABASES") and settings.DATABASES:
                if isinstance(settings.DATABASES, str):
                    databases = json.loads(settings.DATABASES)
                else:
                    databases = settings.DATABASES
            else:
                default_conn = getattr(settings, "DB_CONNECTION_STRING", ":memory:")
                databases = {"default": default_conn}

            for name, conn_str in databases.items():
                adapter = adapter_class(conn_str)
                manager.register_adapter(name, adapter)

        return manager
