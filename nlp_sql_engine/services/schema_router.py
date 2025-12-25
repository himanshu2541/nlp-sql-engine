import numpy as np
from typing import List, Dict, Any, Tuple
from ..core.interfaces.manager import IDatabaseManager
from ..core.interfaces.embedding import IEmbeddingProvider

import logging

logger = logging.getLogger(__name__)


class SchemaRouter:
    """
    Responsibility: Select only the relevant tables for a given user query.
    Mechanism: Semantic Search (RAG) using Embeddings.
    """

    def __init__(self, db_manager: IDatabaseManager, embedder: IEmbeddingProvider):
        self.db_manager = db_manager
        self.embedder = embedder

        # Index: { "db_name.table_name": vector }
        self._index: Dict[str, List[float]] = {}

        # Schemas: { "db_name.table_name": "Table schema string..." }
        self._table_schemas: Dict[str, str] = {}

        # Mapping: "db_name.table_name" -> "db_name"
        self._table_to_db: Dict[str, str] = {}

    def index_tables(self):
        """
        Loads all tables from DB, creates descriptions, and embeds them.
        Call this on application startup.
        """
        print("Indexing schemas from ALL databases...")

        descriptions = []
        keys = []

        # Iterate over all registered databases
        for db_name, adapter in self.db_manager.get_all_adapters().items():
            tables = adapter.get_all_table_names()

            for table in tables:
                schema_str = adapter.get_table_schema(table)

                # Create a unique key for the index
                key = f"{db_name}.{table}"

                # Store Metadata
                self._table_schemas[key] = schema_str
                self._table_to_db[key] = db_name

                # Prepare for embedding
                # We prepend db_name to help context (e.g., "Database: sales. Table: orders")
                desc_for_embed = f"Database: {db_name}\n{schema_str}"
                descriptions.append(desc_for_embed)
                keys.append(key)

        # Batch Embed
        if descriptions:
            vectors = self.embedder.embed_documents(descriptions)
            for key, vector in zip(keys, vectors):
                self._index[key] = vector

        print(
            f"Indexed {len(self._index)} tables across {len(self.db_manager.get_all_adapters())} databases."
        )

    def route(self, question: str, top_k: int = 3) -> Tuple[str, str]:
        """
        Returns (Relevant Schema String, Target Database Name) for the Top-K relevant tables.
        """
        if not self._index:
            self.index_tables()

        q_vector = self.embedder.embed_query(question)

        # Calculate Cosine Similarity
        # (Dot product of normalized vectors)
        scores = []
        for key, t_vector in self._index.items():
            score = np.dot(q_vector, t_vector)
            scores.append((score, key))

        # Sort & Pick Top K
        scores.sort(key=lambda x: x[0], reverse=True)
        top_keys = [key for _, key in scores[:top_k]]

        best_match_key = top_keys[0]
        target_db = self._table_to_db[best_match_key]

        print(
            f"[Router] Query mapped to Database: '{target_db}' (Top match: {best_match_key})"
        )

        # Combine schemas
        combined_schema = "\n\n".join([self._table_schemas[k] for k in top_keys])

        return combined_schema, target_db
