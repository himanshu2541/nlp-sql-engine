from typing import List, Tuple
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.core.interfaces.llm import ILLMProvider

class MockEmbeddingAdapter(IEmbeddingProvider):
    """
    Fake Embedder that returns constant vectors.
    Allows testing the Router logic without an API Key.
    """
    def __init__(self, settings: Settings):
        pass

    def embed_query(self, text: str) -> List[float]:
        # Return a dummy vector of size 10
        return [0.1] * 10

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Return dummy vectors for each document
        return [[0.1] * 10 for _ in texts]

    @property
    def dimension(self) -> int:
        return 10

class SmartMockLLM(ILLMProvider):
    """
    A 'Smarter' Mock LLM that returns valid SQL for our test table.
    """
    def __init__(self, settings: Settings):
        pass

    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        # Always return a valid query for the 'users' table
        return "SELECT id, name, role FROM users;"