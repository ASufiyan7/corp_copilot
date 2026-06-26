import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import DocumentChunk, SourceDocument

def vector_search(
    db: Session,
    query_vector: List[float],
    limit: int = 20,
    ticker: Optional[str] = None,
    filing_type: Optional[str] = None
) -> List[DocumentChunk]:
    """
    Perform semantic search over document chunks using cosine distance on pgvector embeddings.
    Optionally filter by ticker and filing type by joining SourceDocument.
    """
    query = db.query(DocumentChunk)
    
    if ticker or filing_type:
        query = query.join(SourceDocument, DocumentChunk.document_id == SourceDocument.id)
        if ticker:
            # Case-insensitive / exact match. Let's do exact match as ticker is normalized.
            query = query.filter(SourceDocument.ticker == ticker)
        if filing_type:
            query = query.filter(SourceDocument.filing_type == filing_type)
            
    return query.order_by(
        DocumentChunk.embedding.cosine_distance(query_vector)
    ).limit(limit).all()
