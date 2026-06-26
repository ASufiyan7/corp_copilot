import pytest
import uuid
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import SourceDocument, DocumentChunk
from app.database.session import db_url
from app.database import documents
from app.retrieval.embeddings import embedding_service
from app.retrieval.vector_search import vector_search
from app.retrieval.text_search import text_search
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.retriever import retrieve_chunks

@pytest.fixture(scope="session")
def engine():
    return create_engine(db_url)

@pytest.fixture
def db(engine):
    """
    Fixture that provides a database session wrapped in a transaction.
    Rolls back at the end of the test so no test data is persisted.
    """
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_data(db):
    """
    Seed test documents and chunks with real local embeddings and isolated tickers.
    """
    suffix = uuid.uuid4().hex[:6].upper()
    ticker_aapl = f"T_AAPL_{suffix}"
    ticker_nvda = f"T_NVDA_{suffix}"

    # Create Apple Document
    aapl_doc = documents.create_document(
        db,
        ticker=ticker_aapl,
        company_name="Apple Inc.",
        filing_type="10-K",
        filing_date=date(2024, 1, 15),
        content="Apple designs consumer electronics. iPhone sales grew. Services business segment continues to expand margins.",
        source_url="https://sec.gov/aapl"
    )
    
    # Create NVIDIA Document
    nvda_doc = documents.create_document(
        db,
        ticker=ticker_nvda,
        company_name="NVIDIA Corporation",
        filing_type="10-K",
        filing_date=date(2024, 2, 28),
        content="NVIDIA accelerated computing. AI hardware demand is skyrocketing. Data center GPU supply constraints are active.",
        source_url="https://sec.gov/nvda"
    )

    # Chunks text
    aapl_texts = [
        "iPhone revenue reached an all-time record high in late 2023. AAPL_SECRET_TOKEN",
        "Apple services business segment continues to expand margins."
    ]
    nvda_texts = [
        "Artificial intelligence accelerated computing hardware demand is high.",
        "GPU supply constraints affect data center segment revenue. NVDA_SECRET_TOKEN"
    ]

    # Generate real embeddings using embedding service
    aapl_embeddings = embedding_service.embed_texts(aapl_texts)
    nvda_embeddings = embedding_service.embed_texts(nvda_texts)

    # Bulk store
    chunks_data = []
    for i, txt in enumerate(aapl_texts):
        chunks_data.append({
            "document_id": aapl_doc.id,
            "chunk_index": i,
            "chunk_text": txt,
            "embedding": aapl_embeddings[i],
            "chunk_metadata": {"ticker": ticker_aapl, "form": "10-K"}
        })
    for i, txt in enumerate(nvda_texts):
        chunks_data.append({
            "document_id": nvda_doc.id,
            "chunk_index": i,
            "chunk_text": txt,
            "embedding": nvda_embeddings[i],
            "chunk_metadata": {"ticker": ticker_nvda, "form": "10-K"}
        })

    db_chunks = documents.create_document_chunks_bulk(db, chunks_data)
    return {
        "aapl_doc": aapl_doc,
        "nvda_doc": nvda_doc,
        "chunks": db_chunks,
        "ticker_aapl": ticker_aapl,
        "ticker_nvda": ticker_nvda
    }

def test_vector_search_basic(db, sample_data):
    ticker_aapl = sample_data["ticker_aapl"]
    # Search query related to iPhone
    query_text = "iPhone record revenue sales AAPL_SECRET_TOKEN"
    query_vector = embedding_service.embed_text(query_text)
    
    results = vector_search(db, query_vector=query_vector, limit=2)
    
    assert len(results) > 0
    # First result should be Apple-related (Chunk index 0 of AAPL is about iPhone revenue)
    # Filter out external DB matches by only checking if we hit our seeded chunks
    matched = [r for r in results if r.document.ticker == ticker_aapl]
    assert len(matched) > 0
    assert "iPhone" in matched[0].chunk_text

def test_vector_search_filtering(db, sample_data):
    ticker_aapl = sample_data["ticker_aapl"]
    ticker_nvda = sample_data["ticker_nvda"]
    query_text = "AI hardware computing"
    query_vector = embedding_service.embed_text(query_text)
    
    # Run with AAPL filter. Even though the query is about AI/hardware, we filter for AAPL.
    results_aapl = vector_search(db, query_vector=query_vector, limit=2, ticker=ticker_aapl)
    for r in results_aapl:
        assert r.document.ticker == ticker_aapl

    # Run with NVDA filter
    results_nvda = vector_search(db, query_vector=query_vector, limit=2, ticker=ticker_nvda)
    for r in results_nvda:
        assert r.document.ticker == ticker_nvda
    assert "Artificial intelligence" in results_nvda[0].chunk_text

def test_text_search_basic(db, sample_data):
    ticker_nvda = sample_data["ticker_nvda"]
    query = "supply constraints data center NVDA_SECRET_TOKEN"
    results = text_search(db, query=query, limit=2)
    
    assert len(results) >= 1
    # Filter to ensure we only assert on our test NVDA document
    nvda_results = [r for r in results if r.document.ticker == ticker_nvda]
    assert len(nvda_results) >= 1
    assert "supply constraints" in nvda_results[0].chunk_text.lower()

def test_text_search_filtering(db, sample_data):
    ticker_aapl = sample_data["ticker_aapl"]
    ticker_nvda = sample_data["ticker_nvda"]
    query = "margins"
    
    # Filter with NVDA -> should return nothing since "margins" is only in AAPL chunks for our test doc
    results_nvda = text_search(db, query=query, limit=2, ticker=ticker_nvda)
    assert len(results_nvda) == 0

    # Filter with AAPL -> should return AAPL chunk
    results_aapl = text_search(db, query=query, limit=2, ticker=ticker_aapl)
    assert len(results_aapl) == 1
    assert results_aapl[0].document.ticker == ticker_aapl

def test_reciprocal_rank_fusion_logic():
    # Mock DocumentChunks using dummy instances with set ids
    c1 = DocumentChunk(id=uuid.uuid4(), chunk_text="Chunk 1")
    c2 = DocumentChunk(id=uuid.uuid4(), chunk_text="Chunk 2")
    c3 = DocumentChunk(id=uuid.uuid4(), chunk_text="Chunk 3")

    # Semantic ranking: c1, c2, c3
    sem_results = [c1, c2, c3]
    # Lexical ranking: c2, c1
    lex_results = [c2, c1]

    # Run RRF with k=60
    fused = reciprocal_rank_fusion(sem_results, lex_results, k=60, limit=3)
    
    assert len(fused) == 3
    assert fused[0].id in [c1.id, c2.id]
    assert fused[1].id in [c1.id, c2.id]
    assert fused[2].id == c3.id

def test_retrieve_chunks_hybrid(db, sample_data):
    ticker_nvda = sample_data["ticker_nvda"]
    query = "GPU supply constraints in AI compute NVDA_SECRET_TOKEN"
    
    # Retrieve with limit=2 and nvda filter to keep it isolated
    retrieved = retrieve_chunks(db, query=query, limit=2, ticker=ticker_nvda)
    
    assert len(retrieved) <= 2
    assert retrieved[0].document.ticker == ticker_nvda
    assert "GPU" in retrieved[0].chunk_text or "AI" in retrieved[0].chunk_text or "computing" in retrieved[0].chunk_text
