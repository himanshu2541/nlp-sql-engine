from typing import Type, Dict
from src.core.interfaces import ILLMProvider, IEmbeddingProvider, IDatabaseConnector


class ProviderRegistry:
    """
    Singleton registry to hold mappings of names to classes.
    Example: 'openai-gpt4' -> OpenAIAdapter
    """

    _LLM_REGISTRY: Dict[str, Type[ILLMProvider]] = {}
    _EMBED_REGISTRY: Dict[str, Type[IEmbeddingProvider]] = {}
    _DB_REGISTRY: Dict[str, Type[IDatabaseConnector]] = {}

    @classmethod
    def register_llm(cls, name: str):
        """Decorator to register an LLM provider."""

        def inner_wrapper(wrapped_class: Type[ILLMProvider]):
            cls._LLM_REGISTRY[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get_llm_class(cls, name: str) -> Type[ILLMProvider]:
        if name not in cls._LLM_REGISTRY:
            raise ValueError(
                f"LLM Provider '{name}' not found. Available: {list(cls._LLM_REGISTRY.keys())}"
            )
        return cls._LLM_REGISTRY[name]

    @classmethod
    def register_embedding(cls, name: str):
        def inner_wrapper(wrapped_class: Type[IEmbeddingProvider]):
            cls._EMBED_REGISTRY[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get_embedding_class(cls, name: str) -> Type[IEmbeddingProvider]:
        if name not in cls._EMBED_REGISTRY:
            raise ValueError(
                f"Embedding Provider '{name}' not found. Available: {list(cls._EMBED_REGISTRY.keys())}"
            )
        return cls._EMBED_REGISTRY[name]
    
    @classmethod
    def register_db(cls, name: str):
        def inner_wrapper(wrapped_class: Type[IDatabaseConnector]):
            cls._DB_REGISTRY[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get_db_class(cls, name: str) -> Type[IDatabaseConnector]:
        if name not in cls._DB_REGISTRY:
            raise ValueError(
                f"DB Provider '{name}' not found. Available: {list(cls._DB_REGISTRY.keys())}"
            )
        return cls._DB_REGISTRY[name]
