from typing import List
from config.settings import Settings
from src.core.interfaces.embedding import IEmbeddingProvider
from src.app.registries import ProviderRegistry
from langchain_openai import OpenAIEmbeddings
import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_embedding("openai")
class OpenAIEmbeddingAdapter(IEmbeddingProvider):
    def __init__(self, settings: Settings):
        self.api_key = getattr(settings, "API_KEY", None)
        self.model = getattr(settings, "EMBEDDING_MODEL_NAME", "text-embedding-ada-002")

        if not self.api_key:
            logger.error("API_KEY IS NOT SET.")
            raise ValueError("API KEY is not set.")

        self.client = OpenAIEmbeddings(api_key=self.api_key, model=self.model)

    def embed_query(self, text: str) -> List[float]:
        return self.client.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.client.embed_documents(texts)

    @property
    def dimension(self) -> int:
        # text-embedding-ada-002 has 1536 dimensions
        return 1536