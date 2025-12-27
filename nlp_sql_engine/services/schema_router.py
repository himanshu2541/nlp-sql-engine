import numpy as np
from typing import List, Dict, Any, Tuple
from ..core.interfaces.manager import IDatabaseManager
from ..core.interfaces.vector_store import IVectorStore
from nlp_sql_engine.config.settings import Settings

import logging

logger = logging.getLogger(__name__)


class SchemaRouter:
    """
    Responsibility: Select only the relevant tables for a given user query.
    Mechanism: Semantic Search (RAG) using Embeddings.
    """

    def __init__(self, db_manager: IDatabaseManager, vector_store: IVectorStore, settings: Settings):
        self.db_manager = db_manager
        self.vector_store = vector_store
        self._is_indexed = False
        self.settings = settings

    def index_tables(self):
        """
        Loads all tables from DB, creates descriptions, and embeds them.
        Call this on application startup.
        """

        if self._is_indexed:
            return
        print("Indexing schemas from ALL databases...")

        texts, metadatas = [], []

        for db_name, adapter in self.db_manager.get_all_adapters().items():
            for table in adapter.get_all_table_names():
                schema = adapter.get_table_schema(table)

                # We embed: "Database: sales \n Table: orders \n ...columns..."
                texts.append(f"Database: {db_name}\n{schema}")
                metadatas.append({"db_name": db_name, "raw_schema": schema})

        if texts:
            self.vector_store.add_documents(texts, metadatas)

        self._is_indexed = True

    def route(self, question: str, top_k: int = 3) -> Tuple[str, str]:
        """
        Returns (Relevant Schema String, Target Database Name) for the Top-K relevant tables.
        """
        results = self.vector_store.search(question, k=top_k)

        if not results:
            return "", self.settings.DB_MANAGER_ADAPTER  # Default DB

        # Heuristic: The database of the #1 match is the target DB
        best_match_meta = results[0][2]
        target_db = best_match_meta["db_name"]

        # Return combined schemas of top hits (RAG context)
        combined_schema = "\n\n".join([r[2]["raw_schema"] for r in results])

        return combined_schema, target_db
