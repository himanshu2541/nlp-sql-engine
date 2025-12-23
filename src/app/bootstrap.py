from src.app.factories.infrastructure import InfrastructureFactory
from src.app.pipeline import NLPSQLPipeline


def build_pipeline(settings):
    llm = InfrastructureFactory.create_llm(settings)
    db = InfrastructureFactory.create_db("sqlite", ":memory:")
    return NLPSQLPipeline(llm, db)


from src.infra import discover

def discover_adapters():
    discover("src.infra.llm")
    discover("src.infra.database")
    discover("src.infra.embedding")
