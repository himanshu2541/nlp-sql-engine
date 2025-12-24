import numpy as np
from typing import List, Dict, Any
from ..core.interfaces.db import IDatabaseConnector
from ..core.interfaces.embedding import IEmbeddingProvider

import logging
logger = logging.getLogger(__name__)
class SchemaRouter:
    """
    Responsibility: Select only the relevant tables for a given user query.
    Mechanism: Semantic Search (RAG) using Embeddings.
    """
    def __init__(self, db: IDatabaseConnector, embedder: IEmbeddingProvider):
        self.db = db
        self.embedder = embedder
        
        # In-Memory Vector Store for Phase 2
        # Structure: { "table_name": [0.1, 0.5, ...vector...] }
        self._index: Dict[str, List[float]] = {}
        self._table_schemas: Dict[str, str] = {}

    def index_tables(self):
        """
        Loads all tables from DB, creates descriptions, and embeds them.
        Call this on application startup.
        """
        print("Indexing database schema...")
        
        # 1. Get raw table name
        # For now, let's assume get_schema returns a Dict or we parse the full schema string.
        
        # Simulating fetching individual table schemas
        # In a real DB adapter, you'd query information_schema
        tables = self.db.get_all_table_names() 
        
        descriptions = []
        self.table_names = []

        for table in tables:
            # We embed "Table: users, Columns: id, name, age..."
            # This semantic string helps the model match "users" with "people" or "employees"
            schema_str = self.db.get_table_schema(table) 
            self._table_schemas[table] = schema_str
            descriptions.append(schema_str)
            self.table_names.append(table)

        # 2. Batch Embed (Efficient!)
        if descriptions:
            vectors = self.embedder.embed_documents(descriptions)
            
            for name, vector in zip(self.table_names, vectors):
                self._index[name] = vector
        
        print(f"Indexed {len(self._index)} tables.")

    def get_relevant_schemas(self, question: str, top_k: int = 3) -> str:
        """
        Returns the combined schema string for the Top-K relevant tables.
        """
        if not self._index:
            self.index_tables()

        # 1. Embed User Question
        q_vector = self.embedder.embed_query(question)

        # 2. Calculate Cosine Similarity
        # (Dot product of normalized vectors)
        scores = []
        for name, t_vector in self._index.items():
            score = np.dot(q_vector, t_vector) 
            scores.append((score, name))

        # 3. Sort & Pick Top K
        scores.sort(key=lambda x: x[0], reverse=True)
        top_tables = [name for _, name in scores[:top_k]]
        
        logger.info(f"Selected tables: {top_tables}")

        # 4. Return combined schema string
        return "\n\n".join([self._table_schemas[name] for name in top_tables])