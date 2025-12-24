from typing import Any
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.app.registry import ProviderRegistry
from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider


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
