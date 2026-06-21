import pytest
import uuid
from datetime import date
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database.models import Base, Profile, ChatThread, ChatMessage, MessageCitation, SourceDocument, DocumentChunk
from app.database.session import db_url
from app.database import chats, documents

@pytest.fixture(scope="session")
def engine():
    return create_engine(db_url)

@pytest.fixture
def db(engine):
    """
    Fixture that provides a database session wrapped in a transaction.
    At the end of the test, the transaction is rolled back so no test
    data is permanently saved in the database.
    """
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_profile_crud(db):
    # Test Create
    email = f"test_{uuid.uuid4().hex[:8]}@driftwood.com"
    profile_id = uuid.uuid4()
    profile = chats.create_profile(db, email=email, profile_id=profile_id)
    
    assert profile.id == profile_id
    assert profile.email == email
    assert profile.created_at is not None

    # Test Retrieve by ID
    retrieved = chats.get_profile(db, profile_id)
    assert retrieved is not None
    assert retrieved.email == email

    # Test Retrieve by Email
    retrieved_by_email = chats.get_profile_by_email(db, email)
    assert retrieved_by_email is not None
    assert retrieved_by_email.id == profile_id

def test_thread_and_message_crud(db):
    # Setup profile
    email = f"analyst_{uuid.uuid4().hex[:8]}@driftwood.com"
    profile = chats.create_profile(db, email=email)
    
    # Test Thread Create
    thread_id = uuid.uuid4()
    thread = chats.create_thread(db, user_id=profile.id, title="Test Thread", thread_id=thread_id)
    assert thread.id == thread_id
    assert thread.title == "Test Thread"
    assert thread.user_id == profile.id

    # Test Message Create
    user_msg = chats.create_message(db, thread_id=thread_id, role="user", content="Hello, is this working?")
    assert user_msg.role == "user"
    assert user_msg.content == "Hello, is this working?"
    assert user_msg.thread_id == thread_id

    # Verify that the thread's updated_at matches or is after the message created_at
    db.refresh(thread)
    assert thread.updated_at >= user_msg.created_at

    # Create assistant message
    asst_msg = chats.create_message(db, thread_id=thread_id, role="assistant", content="Yes, it works.")
    
    # Test Retrieve messages
    messages = chats.get_messages_by_thread(db, thread_id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"

    # Test Update Title
    updated_thread = chats.update_thread_title(db, thread_id, "Updated Test Thread")
    assert updated_thread.title == "Updated Test Thread"

    # Test List Threads by User
    user_threads = chats.get_threads_by_user(db, profile.id)
    assert len(user_threads) == 1
    assert user_threads[0].id == thread_id

    # Test Delete Thread (cascade)
    success = chats.delete_thread(db, thread_id)
    assert success is True
    assert chats.get_thread(db, thread_id) is None
    # Verify cascade delete of messages
    assert len(db.query(ChatMessage).filter(ChatMessage.thread_id == thread_id).all()) == 0

def test_document_and_chunk_crud(db):
    # Test Document Create
    doc_id = uuid.uuid4()
    doc = documents.create_document(
        db,
        ticker="AAPL",
        company_name="Apple Inc.",
        filing_type="10-K",
        filing_date=date(2024, 1, 15),
        content="This is Apple's 10-K filing content.",
        source_url="https://sec.gov/aapl-10k",
        doc_id=doc_id
    )
    
    assert doc.id == doc_id
    assert doc.ticker == "AAPL"
    assert doc.company_name == "Apple Inc."
    assert doc.filing_type == "10-K"
    assert doc.filing_date == date(2024, 1, 15)
    
    # Test Retrieve Document
    retrieved_doc = documents.get_document(db, doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.ticker == "AAPL"

    retrieved_by_type = documents.get_document_by_ticker_and_type(db, ticker="AAPL", filing_type="10-K")
    assert retrieved_by_type is not None
    assert retrieved_by_type.id == doc_id

    # Test Create Chunks Bulk
    chunks_to_create = [
        {
            "document_id": doc_id,
            "chunk_index": 0,
            "chunk_text": "Apple is a technology company specializing in consumer electronics.",
            "embedding": [0.1] * 384,
            "chunk_metadata": {"page": 1, "section": "Business"}
        },
        {
            "document_id": doc_id,
            "chunk_index": 1,
            "chunk_text": "The company segment revenue for iPhone was significant.",
            "embedding": [0.2] * 384,
            "chunk_metadata": {"page": 5, "section": "Financials"}
        }
    ]
    
    db_chunks = documents.create_document_chunks_bulk(db, chunks_to_create)
    assert len(db_chunks) == 2
    assert db_chunks[0].chunk_index == 0
    assert db_chunks[1].chunk_index == 1

    # Verify retrieved chunks
    retrieved_chunks = documents.get_chunks_by_document(db, doc_id)
    assert len(retrieved_chunks) == 2
    assert retrieved_chunks[0].chunk_text == chunks_to_create[0]["chunk_text"]
    assert retrieved_chunks[1].chunk_metadata == chunks_to_create[1]["chunk_metadata"]

    # Test citations
    email = f"analyst_{uuid.uuid4().hex[:8]}@driftwood.com"
    profile = chats.create_profile(db, email=email)
    thread = chats.create_thread(db, user_id=profile.id, title="Test Citations")
    msg = chats.create_message(db, thread_id=thread.id, role="assistant", content="Apple revenue shift was significant.")
    
    citation = chats.create_citation(db, message_id=msg.id, chunk_id=db_chunks[1].id)
    assert citation.message_id == msg.id
    assert citation.chunk_id == db_chunks[1].id

    msg_citations = chats.get_citations_by_message(db, msg.id)
    assert len(msg_citations) == 1
    assert msg_citations[0].chunk_id == db_chunks[1].id

def test_vector_similarity_search(db):
    doc_id = uuid.uuid4()
    documents.create_document(
        db,
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        filing_type="10-K",
        filing_date=date(2024, 2, 28),
        content="NVIDIA details on AI.",
        doc_id=doc_id
    )

    # Insert two chunks with distinct embeddings
    # Chunk A is closer to [1.0, 0.0, ...]
    # Chunk B is closer to [0.0, 1.0, ...]
    vec_a = [0.0] * 384
    vec_a[0] = 1.0

    vec_b = [0.0] * 384
    vec_b[1] = 1.0

    documents.create_document_chunk(
        db,
        document_id=doc_id,
        chunk_index=0,
        chunk_text="NVIDIA makes GPUs for AI computing.",
        embedding=vec_a,
        chunk_metadata={"source": "A"}
    )
    documents.create_document_chunk(
        db,
        document_id=doc_id,
        chunk_index=1,
        chunk_text="Supply constraints were discussed in risks.",
        embedding=vec_b,
        chunk_metadata={"source": "B"}
    )

    # Search query vector close to vec_a: [0.9, 0.1, 0.0, ...]
    query_vector = [0.0] * 384
    query_vector[0] = 0.9
    query_vector[1] = 0.1

    # Execute cosine distance pgvector search
    results = db.query(DocumentChunk).order_by(
        DocumentChunk.embedding.cosine_distance(query_vector)
    ).limit(2).all()

    assert len(results) >= 2
    # The first result should be Chunk A because its embedding is [1.0, 0.0, ...] which has higher cosine similarity
    # to [0.9, 0.1, 0.0, ...] than Chunk B [0.0, 1.0, ...] has.
    assert results[0].chunk_metadata["source"] == "A"

def test_full_text_search(db):
    doc_id = uuid.uuid4()
    documents.create_document(
        db,
        ticker="MSFT",
        company_name="Microsoft Corp",
        filing_type="10-K",
        filing_date=date(2024, 7, 30),
        content="Microsoft Azure details.",
        doc_id=doc_id
    )

    documents.create_document_chunk(
        db,
        document_id=doc_id,
        chunk_index=0,
        chunk_text="We have experienced rapid growth in Azure AI services.",
        embedding=[0.0] * 384
    )
    documents.create_document_chunk(
        db,
        document_id=doc_id,
        chunk_index=1,
        chunk_text="Global capital expenditures increased for cloud infrastructure.",
        embedding=[0.0] * 384
    )

    # Perform full-text search for 'Azure'
    search_term = "Azure"
    results = db.query(DocumentChunk).filter(
        DocumentChunk.tsvector.op("@@")(func.to_tsquery('english', search_term))
    ).all()

    assert len(results) == 1
    assert "Azure" in results[0].chunk_text
