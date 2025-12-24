from typing import Any, List, Tuple, cast
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.app.registry import ProviderRegistry

from langchain_openai import ChatOpenAI

import logging

logger = logging.getLogger(__name__)


@ProviderRegistry.register_llm("openai")
class OpenAIAdapter(ILLMProvider):
    def __init__(
        self, api_key: str, model_name: str, temperature: float, **kwargs: Any
    ):
        self.api_key = api_key
        self.model = model_name
        self.temperature = temperature

        if not self.api_key:
            logger.error("API_KEY IS NOT SET.")
            raise ValueError("API KEY is not set.")

        # intialize the client
        self.client = ChatOpenAI(
            api_key=lambda: self.api_key, model=self.model, temperature=self.temperature
        )

    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        response = self.client.invoke(messages)
        return cast(str, response.content)
