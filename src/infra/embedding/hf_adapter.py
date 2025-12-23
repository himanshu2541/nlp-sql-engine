from typing import List
from config.settings import Settings
from src.core.interfaces.embedding import IEmbeddingProvider
from src.app.registries import ProviderRegistry
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_embedding("huggingface")
class HuggingFaceEmbeddingAdapter(IEmbeddingProvider):
    def __init__(self, settings: Settings):
        self.model_name = getattr(settings, "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
        self.client = HuggingFaceEmbeddings(model_name=self.model_name)

    def embed_query(self, text: str) -> List[float]:
        return self.client.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.client.embed_documents(texts)

    @property
    def dimension(self) -> int:
        # all-MiniLM-L6-v2 has 384 dimensions
        return 384