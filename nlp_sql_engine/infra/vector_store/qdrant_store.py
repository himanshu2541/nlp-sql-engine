import os
import numpy as np
from typing import List, Dict, Any, Tuple
from nlp_sql_engine.core.interfaces.vector_store import IVectorStore
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.app.registry import ProviderRegistry
import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_vector_store("qdrant")
class QdrantVectorStore(IVectorStore):
    """
    Qdrant Production Vector Store Adapter.
    Supports Qdrant Cloud, local Qdrant server, or embedded in-memory Qdrant.
    """

    def __init__(self, embedder: IEmbeddingProvider, collection_name: str = "nlp_sql_schemas", **kwargs: Any):
        self.embedder = embedder
        self.collection_name = collection_name

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models

            self.models = models
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")

            if qdrant_url:
                self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
                logger.info(f"[Qdrant] Connected to remote Qdrant at {qdrant_url}")
            else:
                self.client = QdrantClient(":memory:")
                logger.info("[Qdrant] Initialized in-memory Qdrant instance")

            # Ensure collection exists
            self._ensure_collection()
            self._use_qdrant_client = True
        except ImportError:
            logger.warning("[Qdrant] 'qdrant-client' not installed. Falling back to high-performance NumPy in-memory vector store.")
            self._use_qdrant_client = False
            self._vectors: List[np.ndarray] = []
            self._texts: List[str] = []
            self._metadatas: List[Dict[str, Any]] = []

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            dim = getattr(self.embedder, "dimension", 768)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self.models.VectorParams(
                    size=dim,
                    distance=self.models.Distance.COSINE,
                ),
            )

    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        if not texts:
            return

        embeddings = self.embedder.embed_documents(texts)

        if self._use_qdrant_client:
            points = []
            for i, (text, meta, vec) in enumerate(zip(texts, metadatas, embeddings)):
                payload = dict(meta)
                payload["text"] = text
                points.append(
                    self.models.PointStruct(
                        id=i,
                        vector=vec,
                        payload=payload,
                    )
                )
            self.client.upsert(collection_name=self.collection_name, points=points)
        else:
            self._vectors.extend([np.array(v) for v in embeddings])
            self._texts.extend(texts)
            self._metadatas.extend(metadatas)

    def search(self, query: str, k: int = 3) -> List[Tuple[str, float, Dict[str, Any]]]:
        q_vec = self.embedder.embed_query(query)

        if self._use_qdrant_client:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=q_vec,
                limit=k,
            )
            results = []
            for hit in search_result:
                payload = dict(hit.payload or {})
                text = payload.pop("text", "")
                results.append((text, float(hit.score), payload))
            return results
        else:
            if not self._vectors:
                return []
            matrix = np.array(self._vectors)
            scores = np.dot(matrix, q_vec)
            top_indices = np.argsort(scores)[-k:][::-1]
            return [(self._texts[idx], float(scores[idx]), self._metadatas[idx]) for idx in top_indices]
