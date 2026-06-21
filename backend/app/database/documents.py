import uuid
from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import SourceDocument, DocumentChunk

# --- SourceDocument CRUD ---

def get_document(db: Session, doc_id: uuid.UUID) -> Optional[SourceDocument]:
    """Retrieve a source document by its UUID."""
    return db.query(SourceDocument).filter(SourceDocument.id == doc_id).first()

def get_document_by_ticker_and_type(
    db: Session, 
    ticker: str, 
    filing_type: str,
    filing_date: Optional[date] = None
) -> Optional[SourceDocument]:
    """Retrieve a document by ticker and filing type, optionally filtered by date."""
    query = db.query(SourceDocument).filter(
        SourceDocument.ticker == ticker,
        SourceDocument.filing_type == filing_type
    )
    if filing_date:
        query = query.filter(SourceDocument.filing_date == filing_date)
    return query.first()

def create_document(
    db: Session,
    ticker: str,
    company_name: str,
    filing_type: str,
    filing_date: date,
    content: str,
    source_url: Optional[str] = None,
    doc_id: Optional[uuid.UUID] = None
) -> SourceDocument:
    """Create a new source document record."""
    new_id = doc_id or uuid.uuid4()
    db_doc = SourceDocument(
        id=new_id,
        ticker=ticker,
        company_name=company_name,
        filing_type=filing_type,
        filing_date=filing_date,
        source_url=source_url,
        content=content
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def delete_document(db: Session, doc_id: uuid.UUID) -> bool:
    """Delete a source document and cascade delete its chunks."""
    db_doc = get_document(db, doc_id)
    if db_doc:
        db.delete(db_doc)
        db.commit()
        return True
    return False

# --- DocumentChunk CRUD ---

def get_chunk(db: Session, chunk_id: uuid.UUID) -> Optional[DocumentChunk]:
    """Retrieve a specific document chunk by its UUID."""
    return db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

def get_chunks_by_document(db: Session, document_id: uuid.UUID) -> List[DocumentChunk]:
    """Retrieve all chunks belonging to a specific source document, sorted by chunk index."""
    return db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_index).all()

def create_document_chunk(
    db: Session,
    document_id: uuid.UUID,
    chunk_index: int,
    chunk_text: str,
    embedding: List[float],
    chunk_metadata: Optional[Dict[str, Any]] = None,
    chunk_id: Optional[uuid.UUID] = None
) -> DocumentChunk:
    """Create a single document chunk."""
    new_id = chunk_id or uuid.uuid4()
    db_chunk = DocumentChunk(
        id=new_id,
        document_id=document_id,
        chunk_index=chunk_index,
        chunk_text=chunk_text,
        embedding=embedding,
        chunk_metadata=chunk_metadata or {}
    )
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk

def create_document_chunks_bulk(
    db: Session,
    chunks_data: List[Dict[str, Any]]
) -> List[DocumentChunk]:
    """
    Bulk create document chunks for high efficiency.
    Each dictionary in chunks_data must have:
      - document_id (UUID)
      - chunk_index (int)
      - chunk_text (str)
      - embedding (List[float])
      - chunk_metadata (dict, optional)
    """
    db_chunks = []
    for chunk in chunks_data:
        new_id = chunk.get("id") or uuid.uuid4()
        db_chunk = DocumentChunk(
            id=new_id,
            document_id=chunk["document_id"],
            chunk_index=chunk["chunk_index"],
            chunk_text=chunk["chunk_text"],
            embedding=chunk["embedding"],
            chunk_metadata=chunk.get("chunk_metadata") or {}
        )
        db_chunks.append(db_chunk)
    
    db.add_all(db_chunks)
    db.commit()
    return db_chunks
