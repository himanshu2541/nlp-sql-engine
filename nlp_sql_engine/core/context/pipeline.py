from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class PipelineContext:
    """
    Holds the state of the generation process.
    Passes through every step of the pipeline.
    """
    question: str
    schema: str
    
    # Intermediate Artifacts
    plan: Optional[str] = None
    sql_query: Optional[str] = None
    
    # Error Handling
    error: Optional[str] = None
    
    # Metadata (e.g., token usage, model names)
    metadata: Dict[str, Any] = field(default_factory=dict)