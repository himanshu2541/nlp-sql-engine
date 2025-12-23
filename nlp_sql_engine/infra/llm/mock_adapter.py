from typing import Any, List, Tuple
from nlp_sql_engine.config.settings import Settings
from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.app.registry import ProviderRegistry

@ProviderRegistry.register_llm("mock")
class MockLLMAdapter(ILLMProvider):
    """Mock LLM Adapter for testing purposes."""

    def __init__(self, settings: Settings):
        pass
    
    def invoke(self, messages: List[Tuple[str, str]]) -> str:
        # Mock response based on messages
        for role, content in messages:
            if role == "user":
                if "user" in content.lower():
                    return "SELECT * FROM users;"
        return "SELECT * FROM users LIMIT 10;"
