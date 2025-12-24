from abc import ABC, abstractmethod
from nlp_sql_engine.core.context.pipeline import PipelineContext

class IPipelineStep(ABC):
    """
    Contract for any step in the SQL generation process.
    Follows Single Responsibility Principle.
    """
    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        pass