from typing import Any
from config.settings import Settings
from src.core.interfaces.llm import ILLMProvider
from src.app.registries import ProviderRegistry
from langchain.chat_models import BaseChatModel


@ProviderRegistry.register_llm("mock")
class MockLLMAdapter(ILLMProvider):
    def create_llm(self, settings: Settings, **kwargs) -> Any:
        return BaseChatModel

    def generate_sql(self, system_prompt: str, user_prompt: str) -> str:
        return "SELECT * FROM mock_table LIMIT 10;"
