import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import DocumentChunk
from app.retrieval.embeddings import embedding_service
from app.retrieval.vector_search import vector_search
from app.retrieval.text_search import text_search
from app.retrieval.fusion import reciprocal_rank_fusion

logger = logging.getLogger(__name__)

def retrieve_chunks(
    db: Session,
    query: str,
    limit: int = 10,
    ticker: Optional[str] = None,
    filing_type: Optional[str] = None
) -> List[DocumentChunk]:
    """
    Unified hybrid retriever orchestrating semantic search, lexical search, and reciprocal rank fusion.
    """
    if not query.strip():
        logger.warning("Empty query received for chunk retrieval.")
        return []
        
    logger.info(
        f"Retrieving chunks for query: '{query}' with filters: "
        f"ticker={ticker}, filing_type={filing_type}"
    )
    
    # Step 1: Embed query using BGE
    query_vector = embedding_service.embed_text(query)
    
    # Step 2: Run semantic search (Top K = 20)
    semantic_results = vector_search(
        db=db,
        query_vector=query_vector,
        limit=20,
        ticker=ticker,
        filing_type=filing_type
    )
    
    # Step 3: Run lexical search (Top K = 20)
    lexical_results = text_search(
        db=db,
        query=query,
        limit=20,
        ticker=ticker,
        filing_type=filing_type
    )
    
    logger.debug(
        f"Retrieved {len(semantic_results)} semantic chunks and "
        f"{len(lexical_results)} lexical chunks."
    )
    
    # Step 4: Reciprocal Rank Fusion & return top 'limit' chunks (default 10)
    fused_results = reciprocal_rank_fusion(
        semantic_results=semantic_results,
        lexical_results=lexical_results,
        k=60,
        limit=limit
    )
    
    logger.info(f"RRF complete. Returning {len(fused_results)} fused chunks.")
    return fused_results
