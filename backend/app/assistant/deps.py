from dataclasses import dataclass
from typing import List
from app.database.models import DocumentChunk

@dataclass
class AgentDeps:
    """
    Dependencies injected into the PydanticAI Agent.
    Contains the retrieved document chunks for grounding.
    """
    retrieved_chunks: List[DocumentChunk]
