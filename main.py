from config.settings import settings
from config.logging import setup_logging
from src.app.bootstrap import build_pipeline, discover_adapters
from src.core.domain.models import NLQuery


def main():
    setup_logging()
    print(f"Hello from {settings.APP_NAME}!")

    # load adapters
    discover_adapters()

    # Create pipeline
    pipeline = build_pipeline(settings)

    # Example query
    nl_query = NLQuery(question="Show me all users")
    result = pipeline.process_query(nl_query)

    print(f"Generated SQL: {result.sql_query.query}")
    print(f"Results: {result.result.rows}")


if __name__ == "__main__":
    main()
