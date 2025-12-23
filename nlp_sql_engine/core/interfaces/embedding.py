from abc import ABC, abstractmethod
from typing import List
from nlp_sql_engine.config.settings import Settings

class IEmbeddingProvider(ABC):
    """
    Interface for Embedding Models.
    Responsibility: Convert text strings into vector representations (lists of floats).
    """

    @abstractmethod
    def __init__(self, settings: Settings):
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Embeds a single query (e.g., the user's question).
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of texts (e.g., table descriptions) in a batch.
        
        Crucial for:
        1. Indexing database schemas efficiently.
        2. Reducing API round-trips (latency).
        """
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Returns the vector dimension size (e.g., 1536 for OpenAI ada-002, 768 for HuggingFace).
        Useful for initializing Vector DB indices correctly.
        """
        pass