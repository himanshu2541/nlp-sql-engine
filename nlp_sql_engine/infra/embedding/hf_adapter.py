from typing import Any, List
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.app.registry import ProviderRegistry
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_embedding("huggingface")
class HuggingFaceEmbeddingAdapter(IEmbeddingProvider):
    def __init__(self, model_name: str, api_key: str, **kwargs: Any):
        self.model_name = model_name
        self.client = HuggingFaceEmbeddings(model_name=self.model_name)

    def embed_query(self, text: str) -> List[float]:
        return self.client.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.client.embed_documents(texts)

    @property
    def dimension(self) -> int:
        return 384