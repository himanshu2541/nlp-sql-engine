import re
from typing import List, Tuple, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from nlp_sql_engine.core.interfaces.llm import ILLMProvider
from nlp_sql_engine.core.interfaces.pipleline import IPipelineStep

class BaseLLMStep(IPipelineStep):
    """Helper base class to handle LLM invocation and cleanup."""
    def __init__(self, llm: ILLMProvider, role_name: str):
        self.llm = llm
        self.role_name = role_name

    def _invoke_llm(self, prompt_template: ChatPromptTemplate, inputs: dict) -> str:
        chain = (
            prompt_template 
            | RunnableLambda(lambda x: self.llm.invoke(self._to_tuples(x)))
            | RunnableLambda(self._clean_response)
        )
        return chain.invoke(inputs)

    def _to_tuples(self, prompt_value: Any) -> List[Tuple[str, str]]:
        # Convert LangChain prompt to Adapter format
        if hasattr(prompt_value, "to_messages"):
            return [(m.type if m.type != "ai" else "assistant", str(m.content)) 
                    for m in prompt_value.to_messages()]
        return []

    def _clean_response(self, text: str) -> str:
        text = text.replace("```sql", "").replace("```", "").strip()
        match = re.search(r"(SELECT|WITH|INSERT|UPDATE|DELETE|DROP)\s+.*?(;|$)", text, re.IGNORECASE | re.DOTALL)
        return match.group(0).strip() if match else text