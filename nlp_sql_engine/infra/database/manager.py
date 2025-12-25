from typing import Dict, List, Optional
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.core.interfaces.manager import IDatabaseManager
from nlp_sql_engine.app.registry import ProviderRegistry

@ProviderRegistry.register_manager("default")
class DatabaseManager(IDatabaseManager):
    """
    Manages multiple database connections.
    """

    def __init__(self):
        self._adapters: Dict[str, IDatabaseConnector] = {}

    def register_adapter(self, name: str, adapter: IDatabaseConnector):
        self._adapters[name] = adapter

    def get_adapter(self, name: str) -> IDatabaseConnector:
        if name not in self._adapters:
            raise ValueError(
                f"Database '{name}' is not registered. Available: {list(self._adapters.keys())}"
            )
        return self._adapters[name]

    def get_all_adapters(self) -> Dict[str, IDatabaseConnector]:
        return self._adapters
