import re
from uuid import UUID
from typing import List
from app.database.models import DocumentChunk
from app.assistant.outputs import GroundedAnswer

class GroundingValidationError(Exception):
    """
    Raised when grounding validation fails.
    """
    pass

def validate_grounding(
    answer: GroundedAnswer,
    retrieved_chunks: List[DocumentChunk]
) -> None:
    """
    Validate that all citations in the GroundedAnswer are valid:
    1. The cited chunk_id must be in the list of retrieved chunks.
    2. The document_id must match the retrieved chunk's document_id.
    3. The excerpt must be non-empty and exist as a substring within the chunk_text.
    """
    retrieved_map = {chunk.id: chunk for chunk in retrieved_chunks}
    
    for idx, citation in enumerate(answer.citations, start=1):
        chunk_id = citation.chunk_id
        doc_id = citation.document_id
        excerpt = citation.excerpt
        
        # Rule 1: Chunk ID check
        if chunk_id not in retrieved_map:
            raise GroundingValidationError(
                f"Grounding validation failed for citation {idx}: "
                f"chunk_id '{chunk_id}' was not in the retrieved context."
            )
            
        chunk = retrieved_map[chunk_id]
        
        # Rule 2: Document ID check
        if chunk.document_id != doc_id:
            raise GroundingValidationError(
                f"Grounding validation failed for citation {idx}: "
                f"document_id '{doc_id}' does not match the retrieved chunk's "
                f"document_id '{chunk.document_id}'."
            )
            
        # Rule 3: Excerpt check
        if not excerpt.strip():
            raise GroundingValidationError(
                f"Grounding validation failed for citation {idx}: "
                f"excerpt is empty."
            )
            
        # Normalize whitespace (replace consecutive newlines/spaces with a single space)
        norm_excerpt = " ".join(excerpt.strip().split())
        norm_chunk_text = " ".join(chunk.chunk_text.strip().split())
        
        if norm_excerpt not in norm_chunk_text:
            raise GroundingValidationError(
                f"Grounding validation failed for citation {idx}: "
                f"excerpt is not a substring of the source chunk text."
            )
