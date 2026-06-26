from typing import List
from app.database.models import DocumentChunk

def reciprocal_rank_fusion(
    semantic_results: List[DocumentChunk],
    lexical_results: List[DocumentChunk],
    k: int = 60,
    limit: int = 10
) -> List[DocumentChunk]:
    """
    Reciprocal Rank Fusion (RRF) rank aggregation.
    Aggregates search results from semantic and lexical search strategies.
    Formula: score = sum(1.0 / (k + rank)) where rank is 1-based.
    """
    scores = {}
    chunk_map = {}
    
    # Process semantic results
    for rank, chunk in enumerate(semantic_results, start=1):
        chunk_id = chunk.id
        chunk_map[chunk_id] = chunk
        scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
        
    # Process lexical results
    for rank, chunk in enumerate(lexical_results, start=1):
        chunk_id = chunk.id
        chunk_map[chunk_id] = chunk
        scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
        
    # Sort chunks by fusion score descending
    sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)
    
    # Return top 'limit' chunks
    return [chunk_map[cid] for cid in sorted_ids[:limit]]
