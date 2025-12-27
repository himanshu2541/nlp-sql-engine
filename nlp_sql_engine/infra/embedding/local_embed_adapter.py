from typing import List, Optional
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.app.registry import ProviderRegistry

# from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_embedding("local")
class LocalEmbeddingAdapter(IEmbeddingProvider):
    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: Optional[str] = "http://localhost:1234/v1",
    ):
        self.api_key = api_key
        self.model = model_name
        self.base_url = base_url

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
