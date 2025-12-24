from langchain_core.prompts import ChatPromptTemplate

from nlp_sql_engine.core.context.pipeline import PipelineContext
from nlp_sql_engine.core.steps.base import BaseLLMStep

import logging

logger = logging.getLogger(__name__)


class PlanningStep(BaseLLMStep):
    def execute(self, context: PipelineContext) -> PipelineContext:
        logger.info(f"   >>> [Step: Planning] using {self.role_name}...")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "user",
                    "### Role: Data Architect\n"
                    "Analyze the user's request and the database schema to create a logical execution plan.\n"
                    "Rules:\n"
                    "1. **Column Mapping:** explicitely identify which column holds the search term. (e.g. 'Laptop' -> `product_name`, 'Electronics' -> `category.name`).\n"
                    "2. **Table Selection:** Only include tables needed for the data or the filter.\n"
                    "3. **Join Strategy:** If data spans multiple tables, explicitly list the Foreign Key connections needed.\n"
                    "\n"
                    "### Schema:\n{schema}\n\n"
                    "### Request:\n{question}\n\n"
                    "### Output:\nPlan:",
                )
            ]
        )

        context.plan = self._invoke_llm(
            prompt, {"schema": context.schema, "question": context.question}
        )
        return context
