from abc import ABC, abstractmethod
from typing import Generator, Any

class IDatabaseConnector(ABC):
    """
    Interface for database interactions.
    Follows Interface Segregation: Keep it focused on execution.
    """
    @abstractmethod
    def get_schema(self) -> str:
        """Returns the schema description for the LLM."""
        pass

    @abstractmethod
    def execute_query(self, query: str) -> Generator[Any, None, None]:
        """
        Executes SQL and yields results row by row.
        Memory efficient handle (Iterator).
        """
        pass