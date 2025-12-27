from langchain_core.prompts import ChatPromptTemplate

from nlp_sql_engine.core.context.pipeline import PipelineContext
from nlp_sql_engine.core.steps.base import BaseLLMStep

import logging

logger = logging.getLogger(__name__)


class PlanningStep(BaseLLMStep):
    def execute(self, context: PipelineContext) -> PipelineContext:
        print(f"   >>> [Step: Planning] using {self.role_name}...")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "user",
                    "### Role: Data Architect\n"
                    "Analyze the user's request and the virtual database schema to create a logical execution plan.\n"
                    "Rules:\n"
                    "1. **Column Mapping:** Explicitly map user terms to specific columns (e.g. 'Laptop' -> `products.product_name`).\n"
                    "2. **Table Selection:** Select the correct virtual tables from the list.\n"
                    "3. **Join Strategy:** Explicitly list the Foreign Key connections needed (e.g. `orders.customer_id` = `customers.id`).\n"
                    "\n"
                    "### Virtual Schema:\n{schema}\n\n"
                    "### Request:\n{question}\n\n"
                    "### Output:\nPlan:",
                )
            ]
        )

        context.plan = self._invoke_llm(
            prompt, {"schema": context.schema, "question": context.question}
        )
        return context
