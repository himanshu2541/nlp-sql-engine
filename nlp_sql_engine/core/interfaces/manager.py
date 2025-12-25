from abc import ABC, abstractmethod
from typing import Dict
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector


class IDatabaseManager(ABC):
    """
    Core interface for managing multiple database connections.
    """

    @abstractmethod
    def register_adapter(self, name: str, adapter: IDatabaseConnector):
        """Register a new database adapter."""
        pass

    @abstractmethod
    def get_adapter(self, name: str) -> IDatabaseConnector:
        """Retrieve a specific database adapter by name."""
        pass

    @abstractmethod
    def get_all_adapters(self) -> Dict[str, IDatabaseConnector]:
        """Retrieve all registered adapters."""
        pass
