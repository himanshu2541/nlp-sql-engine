from abc import ABC, abstractmethod
from typing import Any, List, Tuple
from nlp_sql_engine.config.settings import Settings


class ILLMProvider(ABC):
    """Interface for any Large Language Model."""

    @abstractmethod
    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        **kwargs: Any,
    ):
        pass

    @abstractmethod
    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        pass
