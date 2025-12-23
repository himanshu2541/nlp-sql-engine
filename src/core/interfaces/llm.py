from abc import ABC, abstractmethod
from typing import Any, List, Tuple
from config.settings import Settings


class ILLMProvider(ABC):
    """Interface for any Large Language Model."""

    @abstractmethod
    def __init__(self, settings: Settings):
        pass

    @abstractmethod
    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        pass
