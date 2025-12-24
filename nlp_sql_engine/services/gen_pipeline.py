from typing import List

from nlp_sql_engine.core.context.pipeline import PipelineContext
from nlp_sql_engine.core.interfaces.pipleline import IPipelineStep
from nlp_sql_engine.core.domain.models import SQLQuery


class SQLPipelineService:
    """
    Orchestrator that runs a sequence of steps.
    """

    def __init__(self, steps: List[IPipelineStep]):
        self.steps = steps

    def run(self, schema: str, question: str) -> SQLQuery:
        # Initialize Context
        ctx = PipelineContext(schema=schema, question=question)

        # Run All Steps
        for step in self.steps:
            ctx = step.execute(ctx)

        return self._validate_output(ctx)

    def refine(self, schema: str, question: str, sql: str, error: str) -> SQLQuery:
        """
        Special entry point for the feedback loop.
        In a more advanced setup, this could also be a configurable pipeline.
        """
        ctx = PipelineContext(
            schema=schema, question=question, sql_query=sql, error=error
        )

        # We assume the 'steps' injected include an ErrorCorrectionStep
        # that activates when 'error' is present.
        for step in self.steps:
            ctx = step.execute(ctx)

        return self._validate_output(ctx)
    
    def _validate_output(self, ctx: PipelineContext) -> SQLQuery:
        """
        Ensures we don't pass None to the domain model.
        """
        if not ctx.sql_query:
            # If the pipeline failed to produce SQL, we raise an error.
            # The Use Case will catch this and report it to the user.
            raise ValueError("Pipeline finished but no SQL was generated.")
            
        return SQLQuery(query=ctx.sql_query)
