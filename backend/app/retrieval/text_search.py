import uuid
from typing import List, Optional
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from app.database.models import DocumentChunk, SourceDocument

def text_search(
    db: Session,
    query: str,
    limit: int = 20,
    ticker: Optional[str] = None,
    filing_type: Optional[str] = None
) -> List[DocumentChunk]:
    """
    Perform lexical search over document chunks using full-text search.
    Optionally filter by ticker and filing type by joining SourceDocument.
    """
    if not query.strip():
        return []
        
    tsquery = func.plainto_tsquery('english', query)
    
    db_query = db.query(DocumentChunk).filter(
        DocumentChunk.tsvector.op("@@")(tsquery)
    )
    
    if ticker or filing_type:
        db_query = db_query.join(SourceDocument, DocumentChunk.document_id == SourceDocument.id)
        if ticker:
            db_query = db_query.filter(SourceDocument.ticker == ticker)
        if filing_type:
            db_query = db_query.filter(SourceDocument.filing_type == filing_type)
            
    return db_query.order_by(
        desc(func.ts_rank(DocumentChunk.tsvector, tsquery))
    ).limit(limit).all()
