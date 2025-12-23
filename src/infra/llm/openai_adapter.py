from typing import Any, List, Tuple, cast
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
        self.model = getattr(settings, "LLM_MODEL_NAME", "gpt-4")
        self.temperature = getattr(settings, "LLM_TEMPERATURE", 0.8)

        if not self.api_key:
            logger.error("API_KEY IS NOT SET.")
            raise ValueError("API KEY is not set.")

        # intialize the client
        self.client = ChatOpenAI(
            api_key=self.api_key, model=self.model, temperature=self.temperature
        )

    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        response = self.client.invoke(messages)
        return cast(str, response.content)
