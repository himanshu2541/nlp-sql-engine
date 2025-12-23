from abc import ABC, abstractmethod
from typing import Generator, Any

class IDatabaseConnector(ABC):
    """
    Interface for database interactions.
    Follows Interface Segregation: Keep it focused on execution.
    """
    @abstractmethod
    def __init__(self, connection_string: str):
        pass

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

    @abstractmethod
    def execute_ddl(self, query: str) -> None:
        """Executes DDL statements like CREATE, INSERT, etc."""
        pass