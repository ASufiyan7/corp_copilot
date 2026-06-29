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

def _normalize_text(text: str) -> str:
    """
    Normalize text for comparison by:
    1. Lowercasing.
    2. Stripping quotes, apostrophes, brackets, and parentheses.
    3. Replacing other punctuation (commas, periods, semicolons, etc.) with spaces.
    4. Normalizing consecutive whitespaces into a single space.
    """
    t = text.lower()
    # Remove quotes, apostrophes, brackets, and parentheses
    t = re.sub(r'["\'`“”‘’\[\]\(\)]', '', t)
    # Replace other non-alphanumeric characters with spaces
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    return " ".join(t.split())

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
            
        norm_excerpt = _normalize_text(excerpt)
        norm_chunk_text = _normalize_text(chunk.chunk_text)
        
        if not norm_excerpt:
            raise GroundingValidationError(
                f"Grounding validation failed for citation {idx}: "
                f"excerpt contains no matchable words."
            )
            
        if norm_excerpt not in norm_chunk_text:
            raise GroundingValidationError(
                f"Grounding validation failed for citation {idx}: "
                f"excerpt is not a substring of the source chunk text."
            )

