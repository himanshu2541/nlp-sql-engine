import numpy as np
from typing import List, Dict, Any, Tuple
from nlp_sql_engine.core.interfaces.vector_store import IVectorStore
from nlp_sql_engine.core.interfaces.embedding import IEmbeddingProvider
from nlp_sql_engine.app.registry import ProviderRegistry

@ProviderRegistry.register_vector_store("local")
class LocalVectorStore(IVectorStore):
    def __init__(self, embedder: IEmbeddingProvider):
        self.embedder = embedder
        # In-memory storage
        self._vectors: List[np.ndarray] = []
        self._texts: List[str] = []
        self._metadatas: List[Dict[str, Any]] = []

    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        if not texts: return
        
        # Batch Embed
        embeddings = self.embedder.embed_documents(texts)
        new_vectors = [np.array(vec) for vec in embeddings]
        
        self._vectors.extend(new_vectors)
        self._texts.extend(texts)
        self._metadatas.extend(metadatas)

    def search(self, query: str, k: int = 3) -> List[Tuple[str, float, Dict[str, Any]]]:
        if not self._vectors: return []

        q_vec = self.embedder.embed_query(query)
        
        # Vectorized Cosine Similarity
        matrix = np.array(self._vectors)
        scores = np.dot(matrix, q_vec)
        
        # Get Top-K indices
        top_indices = np.argsort(scores)[-k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append((
                self._texts[idx], 
                float(scores[idx]), 
                self._metadatas[idx]
            ))
        return results