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
        self.model_name = getattr(settings, "LLM_MODEL_NAME", "gpt-4")
        self.base_url = getattr(settings, "LLM_BASE_URL", "http://localhost:1234/v1")
        self.temperature = getattr(settings, "LLM_TEMPERATURE", 0.8)

    def create_llm(self, settings: Settings, **kwargs) -> Any:
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature,
            **kwargs,
        )

    def generate_sql(self, system_prompt: str, user_prompt: str) -> str:
        # Real API logic here
        return f"SELECT * FROM implementation_of_{self.model_name}"
