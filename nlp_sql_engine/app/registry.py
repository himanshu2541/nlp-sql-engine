from typing import Type, Dict
from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.core.interfaces.manager import IDatabaseManager
class ProviderRegistry:
    """
    Central Registry for all infrastructure adapters.
    Uses dictionaries to map string names (e.g. 'openai') to Classes.
    """
    _LLM_REGISTRY: Dict[str, Type[ILLMProvider]] = {}
    _EMBED_REGISTRY: Dict[str, Type[IEmbeddingProvider]] = {}
    _DB_REGISTRY: Dict[str, Type[IDatabaseConnector]] = {}
    _DB_MANAGER_REGISTRY: Dict[str, Type[IDatabaseManager]] = {}

    # --- LLM Registration ---
    @classmethod
    def register_llm(cls, name: str):
        def inner_wrapper(wrapped_class: Type[ILLMProvider]):
            cls._LLM_REGISTRY[name] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def get_llm_class(cls, name: str) -> Type[ILLMProvider]:
        if name not in cls._LLM_REGISTRY:
            raise ValueError(f"LLM '{name}' not found. Registered: {list(cls._LLM_REGISTRY.keys())}")
        return cls._LLM_REGISTRY[name]

    # --- Embedding Registration ---
    @classmethod
    def register_embedding(cls, name: str):
        def inner_wrapper(wrapped_class: Type[IEmbeddingProvider]):
            cls._EMBED_REGISTRY[name] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def get_embedding_class(cls, name: str) -> Type[IEmbeddingProvider]:
        if name not in cls._EMBED_REGISTRY:
            raise ValueError(f"Embedding '{name}' not found. Registered: {list(cls._EMBED_REGISTRY.keys())}")
        return cls._EMBED_REGISTRY[name]

    # --- Database Registration ---
    @classmethod
    def register_db(cls, name: str):
        def inner_wrapper(wrapped_class: Type[IDatabaseConnector]):
            cls._DB_REGISTRY[name] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def get_db_class(cls, name: str) -> Type[IDatabaseConnector]:
        if name not in cls._DB_REGISTRY:
            raise ValueError(f"Database '{name}' not found. Registered: {list(cls._DB_REGISTRY.keys())}")
        return cls._DB_REGISTRY[name]
    
    # --- Database Manager Registration ---
    @classmethod
    def register_manager(cls, name: str):
        def inner_wrapper(wrapped_class: Type[IDatabaseManager]):
            cls._DB_MANAGER_REGISTRY[name] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def get_manager_class(cls, name: str) -> Type[IDatabaseManager]:
        if name not in cls._DB_MANAGER_REGISTRY:
            raise ValueError(f"Manager '{name}' not found. Registered: {list(cls._DB_MANAGER_REGISTRY.keys())}")
        return cls._DB_MANAGER_REGISTRY[name]