import pytest
from app.retrieval.embeddings import embedding_service
from app.config import settings

def cosine_similarity(v1, v2):
    dot_product = sum(x*y for x, y in zip(v1, v2))
    magnitude_v1 = sum(x*x for x in v1) ** 0.5
    magnitude_v2 = sum(x*x for x in v2) ** 0.5
    if magnitude_v1 * magnitude_v2 == 0:
        return 0.0
    return dot_product / (magnitude_v1 * magnitude_v2)

def test_embed_text_dimensions():
    text = "NVIDIA is a leader in accelerated computing and AI."
    embedding = embedding_service.embed_text(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == settings.embedding_dimensions
    assert all(isinstance(val, float) for val in embedding)

def test_embed_texts_bulk():
    texts = [
        "Apple reports record high services revenue.",
        "Amazon AWS operating margin expansion.",
        "Alphabet search traffic increases."
    ]
    embeddings = embedding_service.embed_texts(texts)
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == 3
    for emb in embeddings:
        assert isinstance(emb, list)
        assert len(emb) == settings.embedding_dimensions

def test_embedding_semantic_quality():
    # Semantically related sentences
    s1 = "AI demand is skyrocketing and cloud infrastructure constraints are real."
    s2 = "Artificial intelligence hardware is in high demand and Azure faces capacity shortages."
    # Unrelated sentence
    s3 = "Corporate travel policies have been revised to reduce operational expenses."
    
    emb1 = embedding_service.embed_text(s1)
    emb2 = embedding_service.embed_text(s2)
    emb3 = embedding_service.embed_text(s3)
    
    sim_related = cosine_similarity(emb1, emb2)
    sim_unrelated = cosine_similarity(emb1, emb3)
    
    # Cosine similarity between related sentences should be higher than unrelated ones
    assert sim_related > sim_unrelated
