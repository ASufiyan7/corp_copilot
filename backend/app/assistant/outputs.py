from uuid import UUID
from typing import List
from pydantic import BaseModel, Field

class Citation(BaseModel):
    """
    Model representing a citation to a specific source document chunk.
    """
    chunk_id: UUID = Field(description="The UUID of the cited document chunk.")
    document_id: UUID = Field(description="The UUID of the source document.")
    excerpt: str = Field(description="The exact quote or short excerpt from the chunk text supporting the claim.")

class GroundedAnswer(BaseModel):
    """
    Structured response containing the grounded answer and its citations.
    """
    answer: str = Field(description="The natural language answer to the user's question, grounded strictly in the provided context.")
    citations: List[Citation] = Field(description="List of citations mapping factual claims in the answer to the source chunks.")
    supporting_passages: List[str] = Field(description="Excerpts or text passages from the chunks that support the answer.")
