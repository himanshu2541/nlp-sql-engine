from typing import Generator, Any
from nlp_sql_engine.core.interfaces.db import IDatabaseConnector
from nlp_sql_engine.services.sql_generator import SQLGenerationService
from nlp_sql_engine.core.domain.models import NLQuery, PipelineResult, QueryResult


class AskQuestionUseCase:
    def __init__(self, db: IDatabaseConnector, sql_service: SQLGenerationService):
        self.db = db
        self.sql_service = sql_service

    def execute(self, query: NLQuery) -> Generator[PipelineResult, None, None]:
        schema = self.db.get_schema()

        sql_query = self.sql_service.generate_sql(schema, query.question)

        # Execute & Stream
        # We yield the result so the caller (API/CLI) controls the flow
        try:
            row_iterator = self.db.execute_query(sql_query.query)
            # Create a result object that holds the iterator, NOT the list
            result_wrapper = QueryResult(columns=[], rows=row_iterator)
            yield PipelineResult(sql_query=sql_query, result=result_wrapper)

        except Exception as e:
            # Handle error
            yield PipelineResult(error=str(e))
