from typing import Any, List, Tuple
from config.settings import Settings
from src.core.interfaces.llm import ILLMProvider
from src.app.registries import ProviderRegistry

@ProviderRegistry.register_llm("mock")
class MockLLMAdapter(ILLMProvider):
    """Mock LLM Adapter for testing purposes."""

    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        # Mock response based on messages
        for role, content in messages:
            if role == "user":
                if "user" in content.lower():
                    return "SELECT * FROM users;"
        return "SELECT * FROM users LIMIT 10;"
