# src/app/factory.py
import os
from typing import Type
from src.app.registries import ProviderRegistry
from src.core.interfaces.llm import ILLMProvider
from src.core.interfaces.embedding import IEmbeddingProvider
from src.core.interfaces.db import IDatabaseConnector

from config.settings import Settings

class InfrastructureFactory:
    @staticmethod
    def create_llm(settings: Settings) -> ILLMProvider:
        provider = getattr(settings, "LLM_PROVIDER", "phi3-mini").lower()
        cls = ProviderRegistry.get_llm_class(provider)
        return cls(settings)

    @staticmethod
    def create_embedding(settings: Settings) -> IEmbeddingProvider:
        provider = getattr(settings, "EMBEDDING_PROVIDER", "huggingface").lower()
        try:
            cls = ProviderRegistry.get_embedding_class(provider)
            return cls()
        except ValueError:
            # Fallback to mock or raise
            raise ValueError(f"Embedding provider '{provider}' not available. Install required dependencies.")

    @staticmethod
    def create_db(name: str, connection_string: str) -> IDatabaseConnector:
        cls = ProviderRegistry.get_db_class(name)
        return cls(connection_string)