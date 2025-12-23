from abc import ABC, abstractmethod
from typing import Any
from config.settings import Settings

class ILLMProvider(ABC):
    """Interface for any Large Language Model."""

    @abstractmethod
    def create_llm(self, settings: Settings) -> Any:
        """
        Creates and returns configured LLM object (e.g., ChatOpenAI)
        """
        pass
    
    @abstractmethod
    def generate_sql(self, system_prompt: str, user_prompt: str) -> str:
        pass