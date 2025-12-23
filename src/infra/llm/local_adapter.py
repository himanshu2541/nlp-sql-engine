from typing import Any, List, Tuple, cast
from config.settings import Settings
from src.core.interfaces.llm import ILLMProvider
from src.app.registries import ProviderRegistry

from langchain_openai import ChatOpenAI
from langchain.chat_models import BaseChatModel

import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_llm("local")
class LocalLLMAdapter(ILLMProvider):
    def __init__(self, settings: Settings):
        self.api_key = getattr(settings, "API_KEY", "type-your-api-key-here")
        self.model_name = getattr(settings, "LLM_MODEL_NAME", "phi-3-mini-4k-instruct")
        self.base_url = getattr(settings, "LLM_BASE_URL", "http://localhost:1234/v1")
        self.temperature = getattr(settings, "LLM_TEMPERATURE", 0.8)

        self.client = self._create_llm()

    def _create_llm(self) -> BaseChatModel:
        return ChatOpenAI(
            api_key=lambda: self.api_key, # LM-studio ignores it.
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature,
        )

    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        response = self.client.invoke(messages)
        return cast(str, response.content)