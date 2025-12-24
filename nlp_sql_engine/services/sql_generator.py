import re
from operator import itemgetter
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from nlp_sql_engine.core.domain.models import SQLQuery
from nlp_sql_engine.core.interfaces.llm import ILLMProvider

from typing import Any, List, Tuple


class SQLGenerationService:
    def __init__(self, llm: ILLMProvider):
        self.llm = RunnableLambda(lambda x: llm.invoke(self._to_tuples(x)))

    def generate(self, schema: str, question: str) -> SQLQuery:
        template = ChatPromptTemplate.from_messages(
            [
                (
                    "user",
                    "### Instructions:\n"
                    "You are a SQL expert. Convert the user's question into a standard SQL query.\n"
                    "Rules:\n"
                    "1. **Output:** Output ONLY the raw SQL query. No Markdown. No Explanations.\n"
                    "2. **Thinking Process:** Briefly analyze tables. If data is across multiple tables, you MUST plan a JOIN using Foreign Keys.\n"
                    "3. **Text Smarts:** NEVER use '=' for strings. ALWAYS use `LIKE '%value%'` for case-insensitive matching. Correct user typos (e.g., 'Coffe' -> 'Coffee') inside the SQL.\n"
                    "4. **Dates:** Use `strftime` for partial dates: `strftime('%Y', col) = '2023'`, `strftime('%m', col) = '04'`, `strftime('%d', col) = '10'`.\n"
                    "5. **Aggregations:** Use `GROUP BY` with `COUNT`, `SUM`, `AVG` for summary questions.\n"
                    "6. **Ordering:** Use `ORDER BY DESC/ASC` for 'top', 'latest', 'best', or sorted results.\n"
                    "7. **Safety:** Generate `SELECT` queries ONLY. Default to `LIMIT 100` if the user asks for 'all' records to prevent overflows.\n"
                    "8. **Schema Loyalty:** Use exact column names from the schema. Use table aliases (e.g., `c` for customers) for clarity.\n"
                    "9. **Logic:** Handle multiple conditions with `AND`/`OR`. Handle missing data with `IS NULL`.\n"
                    "10. **Defaults:** If ambiguous, assume the most common interpretation (e.g., 'show orders' -> `SELECT * FROM orders`).\n"
                    "\n"
                    "### Database Schema:\n"
                    "{schema}\n\n"
                    "### Example 1 (Fuzzy Match & Spelling):\n"
                    "Question: Find orders by Alice Smith\n"
                    "Thinking: Need `orders` and `customers`. Join on `customer_id`. The name might be 'Alice Smith' or 'AliceSmith', so I will use LIKE.\n"
                    "SQL: SELECT o.* FROM orders o JOIN customers c ON o.customer_id = c.id WHERE c.name LIKE '%Alice%Smith%';\n\n"
                    "### Example 2 (Complex Join & Aggregation):\n"
                    "Question: Total sales per category\n"
                    "Thinking: Join `order_items`, `products`, and `categories`. Sum `quantity * unit_price`. Group by category name.\n"
                    "SQL: SELECT c.name, SUM(oi.quantity * oi.unit_price) as total_sales FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN categories c ON p.category_id = c.id GROUP BY c.name;\n\n"
                    "### Actual Request:\n"
                    "Question: {question}\n"
                    "Thinking:",
                )
            ]
        )

        clean_sql_step = RunnableLambda(self._clean_sql)

        chain = template | self.llm | StrOutputParser() | clean_sql_step

        clean_sql = chain.invoke({"schema": schema, "question": question})
        return SQLQuery(query=clean_sql)

    def _to_tuples(self, prompt_value: Any) -> List[Tuple[str, str]]:
        """
        Adapts LangChain's 'ChatPromptValue' to our Core 'List[Tuple]' format.
        """
        # Ensure we have a standard list of messages
        if hasattr(prompt_value, "to_messages"):
            messages = prompt_value.to_messages()
        else:
            return []

        formatted_messages = []
        for m in messages:
            # Map LangChain types to your simple strings
            role = "user"
            if m.type == "system":
                role = "system"
            elif m.type == "ai":
                role = "assistant"

            formatted_messages.append((role, str(m.content)))

        return formatted_messages

    def _clean_sql(self, text: str) -> str:
        """
        Pure function to extract SQL from text.
        Used as a RunnableLambda step.
        """
        # Strip markdown
        text = text.replace("```sql", "").replace("```", "").strip()

        # Regex extraction
        match = re.search(
            r"(SELECT|WITH|INSERT|UPDATE|DELETE|DROP)\s+.*?(;|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if match:
            return match.group(0).strip()

        return text
