import json
import urllib.request
import urllib.error
from typing import Any, List, Optional
import logging
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.app.registry import ProviderRegistry

logger = logging.getLogger(__name__)


@ProviderRegistry.register_embedding("gemini")
@ProviderRegistry.register_embedding("google")
class GeminiEmbeddingAdapter(IEmbeddingProvider):
    """
    Google Gemini Free Embedding Adapter using text-embedding-004.
    Uses Google AI Studio's native REST API.
    Free tier allows 1,500 requests/day at zero cost.
    """

    def __init__(
        self,
        model_name: str = "gemini-embedding-001",
        api_key: str = "",
        **kwargs: Any,
    ):
        # Strip any 'models/' prefix if present
        clean_model = (model_name or "gemini-embedding-001").replace("models/", "")
        if clean_model in ["text-embedding-004", "embedding-001"]:
            clean_model = "gemini-embedding-001"
        self.model = clean_model
        self.api_key = api_key.strip() if api_key else ""
        self._dimension: int = 3072


        if not self.api_key:
            logger.warning("Gemini API key is empty. Set GEMINI_API_KEY or EMBEDDING_API_KEY in .env.")

    def _ensure_dimension(self, embedding: List[float]) -> None:
        if embedding:
            self._dimension = len(embedding)

    def embed_query(self, text: str) -> List[float]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in .env.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent?key={self.api_key}"
        payload = {
            "model": f"models/{self.model}",
            "content": {
                "parts": [{"text": text}]
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                vec = data["embedding"]["values"]
                self._ensure_dimension(vec)
                return vec
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"Gemini embedding API error: {e.code} - {err_body}")
            raise RuntimeError(f"Gemini embedding API error ({e.code}): {err_body}") from e
        except Exception as e:
            logger.error(f"Failed to generate Gemini embedding for query: {e}")
            raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in .env.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:batchEmbedContents?key={self.api_key}"
        requests_list = [
            {
                "model": f"models/{self.model}",
                "content": {"parts": [{"text": t}]},
            }
            for t in texts
        ]

        payload = {"requests": requests_list}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
                embeddings = [item["values"] for item in data["embeddings"]]
                if embeddings:
                    self._ensure_dimension(embeddings[0])
                return embeddings
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"Gemini batch embedding API error: {e.code} - {err_body}")
            raise RuntimeError(f"Gemini batch embedding API error ({e.code}): {err_body}") from e
        except Exception as e:
            logger.error(f"Failed to batch embed documents with Gemini: {e}")
            raise e

    @property
    def dimension(self) -> int:
        return self._dimension

