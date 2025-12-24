from typing import Any, List, Tuple, cast
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.app.registry import ProviderRegistry

from langchain_openai import ChatOpenAI
from langchain.chat_models import BaseChatModel

import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_llm("local")
class LocalLLMAdapter(ILLMProvider):
    def __init__(self, api_key: str, model_name: str, temperature: float, **kwargs: Any):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = kwargs.get("base_url", "http://localhost:1234/v1")
        self.temperature = temperature
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