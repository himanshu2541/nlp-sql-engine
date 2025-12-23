from typing import Any
from config.settings import Settings
from src.core.interfaces.llm import ILLMProvider
from src.app.registries import ProviderRegistry

from langchain_openai import ChatOpenAI

import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_llm("openai")
class OpenAIAdapter(ILLMProvider):
    def __init__(self, settings: Settings):
        self.api_key = getattr(settings, "API_KEY", None)
        self.model_name = getattr(settings, "MODEL_NAME", "gpt-4")
        self.temperature = getattr(settings, "TEMPERATURE", 0.8)

        if not self.api_key:
            logger.error("API_KEY IS NOT SET.")
            raise ValueError("API KEY is not set.")

    def create_llm(self, settings: Settings, **kwargs) -> Any:
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
            temperature=self.temperature,
            **kwargs,
        )

    def generate_sql(self, system_prompt: str, user_prompt: str) -> str:
        # Real API logic here
        return f"SELECT * FROM implementation_of_{self.model_name}"
