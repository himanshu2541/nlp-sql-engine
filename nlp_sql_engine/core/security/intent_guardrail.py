import re
from typing import Optional, Tuple

class IntentGuardrail:
    """
    Classifies user intent to intercept greetings, help requests,
    and out-of-domain prompts before invoking costly SQL generation pipelines.
    """

    GREETING_PATTERNS = [
        r"^(hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening|greetings|hola|namaste)\b[!.]*$",
        r"^(howdy|what'?s\s+up|sup)\b[!.]*$",
    ]

    HELP_PATTERNS = [
        r"^(help|what\s+can\s+you\s+do|how\s+to\s+use|capabilities|commands)\b[?.]*$",
        r"^(what\s+tables|list\s+tables|show\s+databases|available\s+tables)\b[?.]*$",
    ]

    OFF_TOPIC_PATTERNS = [
        r"^(tell\s+me\s+a\s+joke|who\s+are\s+you|what\s+is\s+your\s+name|how\s+is\s+the\s+weather|write\s+a\s+poem|sing\s+a\s+song)\b[?.]*$",
    ]

    @classmethod
    def evaluate(cls, user_text: str) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_non_query, response_message).
        If is_non_query is True, execution should return response_message directly.
        """
        cleaned = user_text.strip().lower()

        # 1. Empty or single punctuation
        if not cleaned or len(cleaned) <= 1:
            return True, "Please enter a database question (e.g., 'What products cost more than $100?')."

        # 2. Greeting Check
        for pattern in cls.GREETING_PATTERNS:
            if re.match(pattern, cleaned, re.IGNORECASE):
                return True, (
                    "Hello! I am your NLP-SQL Engine.\n"
                    "I can query and join across CRM, Inventory, and Sales databases.\n\n"
                    "Try asking:\n"
                    "- 'What products cost more than $100?'\n"
                    "- 'List customer names and their order IDs.'\n"
                    "- 'Show product names and their average rating.'"
                )

        # 3. Help Check
        for pattern in cls.HELP_PATTERNS:
            if re.match(pattern, cleaned, re.IGNORECASE):
                return True, (
                    "NLP-SQL Engine Help:\n"
                    "Connected Databases:\n"
                    "- crm.db: customers, reviews\n"
                    "- inventory.db: products, categories, suppliers\n"
                    "- sales.db: orders, order_items, payments\n\n"
                    "Just ask any question in natural language!"
                )

        # 4. Off-topic Check
        for pattern in cls.OFF_TOPIC_PATTERNS:
            if re.match(pattern, cleaned, re.IGNORECASE):
                return True, (
                    "I am a specialized SQL Database Assistant.\n"
                    "I cannot perform general chat, but I can execute natural language queries across your databases."
                )


        # Pass through to SQL pipeline
        return False, None
