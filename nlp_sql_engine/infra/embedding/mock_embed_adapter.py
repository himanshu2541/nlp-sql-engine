import hashlib
import numpy as np
from typing import Any, List
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.app.registry import ProviderRegistry


@ProviderRegistry.register_embedding("mock")
class MockEmbeddingAdapter(IEmbeddingProvider):
    """
    Lightweight keyword/hash-based embedder for offline/free testing without external APIs or heavy models.
    """

    def __init__(self, model_name: str = "mock-embed", api_key: str = "", **kwargs: Any):
        self.model_name = model_name
        self._dim = 64

    def _hash_text(self, text: str) -> List[float]:
        tokens = text.lower().split()
        vec = np.zeros(self._dim, dtype=np.float32)
        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_query(self, text: str) -> List[float]:
        return self._hash_text(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_text(t) for t in texts]

    @property
    def dimension(self) -> int:
        return self._dim
