from config.settings import Settings
from src.app.registries import ProviderRegistry

class LLMFactory:
  """
  Factory to retrieve LLM strategies.
  """
  @staticmethod
  def get_llm(settings: Settings):
    provider = getattr(settings, "LLM_PROVIDER", "phi-3-mini")

    strategy_cls = ProviderRegistry.get_llm_class(provider)
    return strategy_cls()