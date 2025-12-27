from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from .embedding import IEmbeddingProvider

class IVectorStore(ABC):
    """
    Abstracts the storage and retrieval of semantic embeddings.
    """

    @abstractmethod
    def __init__(self, embedder: IEmbeddingProvider, **kwargs):
        """
        Allows to send any kwargs
        """
        pass
    
    @abstractmethod
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Embeds and stores text documents with associated metadata.
        """
        pass

    @abstractmethod
    def search(self, query: str, k: int = 3) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Semantically searches for documents.
        Returns: List of (Document Text, Score, Metadata)
        """
        pass