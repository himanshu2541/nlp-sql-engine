import os
import numpy as np
from typing import List, Dict, Any, Tuple
from nlp_sql_engine.core.interfaces.vector_store import IVectorStore
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.app.registry import ProviderRegistry
import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_vector_store("pinecone")
class PineconeVectorStore(IVectorStore):
    """
    Pinecone Production Vector Store Adapter.
    """

    def __init__(self, embedder: IEmbeddingProvider, index_name: str = "nlp-sql-schemas", **kwargs: Any):
        self.embedder = embedder
        self.index_name = index_name

        try:
            from pinecone import Pinecone

            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY environment variable is missing.")

            pc = Pinecone(api_key=api_key)
            self.index = pc.Index(self.index_name)
            self._use_pinecone = True
            logger.info(f"[Pinecone] Connected to index '{self.index_name}'")
        except Exception as e:
            logger.warning(f"[Pinecone] Initialization fallback due to: {e}")
            self._use_pinecone = False
            self._vectors: List[np.ndarray] = []
            self._texts: List[str] = []
            self._metadatas: List[Dict[str, Any]] = []

    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        if not texts:
            return

        embeddings = self.embedder.embed_documents(texts)

        if self._use_pinecone:
            vectors_to_upsert = []
            for i, (text, meta, vec) in enumerate(zip(texts, metadatas, embeddings)):
                payload = dict(meta)
                payload["text"] = text
                vectors_to_upsert.append({
                    "id": f"doc_{i}",
                    "values": vec,
                    "metadata": payload
                })
            self.index.upsert(vectors=vectors_to_upsert)
        else:
            self._vectors.extend([np.array(v) for v in embeddings])
            self._texts.extend(texts)
            self._metadatas.extend(metadatas)

    def search(self, query: str, k: int = 3) -> List[Tuple[str, float, Dict[str, Any]]]:
        q_vec = self.embedder.embed_query(query)

        if self._use_pinecone:
            response = self.index.query(vector=q_vec, top_k=k, include_metadata=True)
            results = []
            for match in response.get("matches", []):
                meta = match.get("metadata", {})
                text = meta.pop("text", "")
                results.append((text, float(match.get("score", 0.0)), meta))
            return results
        else:
            if not self._vectors:
                return []
            matrix = np.array(self._vectors)
            scores = np.dot(matrix, q_vec)
            top_indices = np.argsort(scores)[-k:][::-1]
            return [(self._texts[idx], float(scores[idx]), self._metadatas[idx]) for idx in top_indices]
