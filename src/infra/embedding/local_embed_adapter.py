from typing import List, Optional
from config.settings import Settings
from src.core.interfaces.embedding import IEmbeddingProvider
from src.app.registries import ProviderRegistry

# from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_embedding("local")
class LocalEmbeddingAdapter(IEmbeddingProvider):
    def __init__(self, settings: Settings):
        self.api_key = getattr(settings, "EMBEDDING_API_KEY", None)
        self.model = getattr(settings, "EMBEDDING_MODEL_NAME", "")
        self.base_url = getattr(settings, "EMBEDDING_BASE_URL", None)

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        self._dimension: Optional[int] = None

    def _ensure_dimension(self, embedding: List[float]) -> None:
        if self._dimension is None:
            self._dimension = len(embedding)

    def embed_query(self, text: str) -> List[float]:
        res = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        vec = res.data[0].embedding
        self._ensure_dimension(vec)
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        res = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        embeddings = [d.embedding for d in res.data]
        self._ensure_dimension(embeddings[0])
        return embeddings

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            raise RuntimeError(
                "Embedding dimension not initialized. "
                "Call embed_query() once at startup."
            )
        return self._dimension
