import pytest
import uuid
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import db_url
from app.database.models import SourceDocument, DocumentChunk
from app.database import documents
from app.ingestion.parser import strip_html, chunk_text

@pytest.fixture(scope="session")
def engine():
    return create_engine(db_url)

@pytest.fixture
def db(engine):
    """
    Transaction-wrapped db session. Automatically rolls back at the end of each test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_strip_html():
    html = """
    <html>
        <head>
            <title>Skip Me</title>
            <style>
                body { color: red; }
            </style>
        </head>
        <body>
            <h1>Apple Inc.</h1>
            <p>This is a <b>paragraph</b> introducing the business.</p>
            <div>Some segment info.</div>
            <script>
                console.log("Ignore me too");
            </script>
            <table>
                <tr>
                    <td>Row 1 Col 1</td>
                    <td>Row 1 Col 2</td>
                </tr>
            </table>
        </body>
    </html>
    """
    text = strip_html(html)
    
    # Assertions
    assert "Skip Me" not in text
    assert "color: red" not in text
    assert "console.log" not in text
    assert "Apple Inc." in text
    assert "This is a paragraph introducing the business." in text
    assert "Some segment info." in text
    assert "Row 1 Col 1" in text
    assert "Row 1 Col 2" in text
    
    # Check that block boundaries insert whitespace (not concatenated directly)
    import re
    assert re.search(r"introducing the business\.\s+Some segment info\.", text) is not None

def test_chunk_text():
    # Construct a string of length 3500 chars (representing SEC text)
    text = " ".join([f"Word{i:04d}" for i in range(500)]) # Word0000 Word0001 ... (each is 9 chars with space)
    # total len = ~4500 chars
    
    chunks = chunk_text(text, chunk_size=1000, overlap=150)
    
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        # Target size 1000, max allowed size 1200
        # If it's the last chunk, it might be smaller, but other chunks should be within boundaries.
        if i < len(chunks) - 1:
            assert 1000 <= len(chunk) <= 1200
            
    # Verify that the entire text is covered and overlap exists
    # We can reconstruct or check overlap: next chunk should start with trailing words of previous chunk.
    for idx in range(len(chunks) - 1):
        curr_chunk = chunks[idx]
        next_chunk = chunks[idx + 1]
        
        # Check that there is common text between the end of curr_chunk and start of next_chunk
        # The overlap length should be approximately 150 (could vary slightly due to word boundary)
        overlap_part = curr_chunk[-100:]
        assert overlap_part in next_chunk

def test_db_ingestion_and_overwrite(db):
    ticker = f"TEST_NVDA_{uuid.uuid4().hex[:4].upper()}"
    form = "10-K"
    filing_date = date(2025, 2, 26)
    
    # 1. Store first filing version
    doc1 = documents.create_document(
        db=db,
        ticker=ticker,
        company_name="NVIDIA Corporation",
        filing_type=form,
        filing_date=filing_date,
        content="First version content with some details."
    )
    
    # Store some chunks for doc1
    chunks_data1 = [
        {
            "document_id": doc1.id,
            "chunk_index": 0,
            "chunk_text": "First version content with some details.",
            "embedding": [0.0] * 384,
            "chunk_metadata": {"ticker": ticker}
        }
    ]
    documents.create_document_chunks_bulk(db, chunks_data1)
    
    # Verify stored
    assert documents.get_document(db, doc1.id) is not None
    assert len(documents.get_chunks_by_document(db, doc1.id)) == 1
    
    # 2. Re-ingest the same filing to test overwrite/idempotency
    # In pipeline.py, if a document already exists for the same ticker, filing_type, and filing_date,
    # it gets deleted first.
    existing_doc = documents.get_document_by_ticker_and_type(
        db=db,
        ticker=ticker,
        filing_type=form,
        filing_date=filing_date
    )
    assert existing_doc is not None
    assert existing_doc.id == doc1.id
    
    # Delete and re-create
    documents.delete_document(db, existing_doc.id)
    
    # Verify cascade delete of chunks
    assert documents.get_document(db, doc1.id) is None
    # Let's count matching chunks in DB directly
    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc1.id).count()
    assert chunk_count == 0
    
    # Insert new version
    doc2 = documents.create_document(
        db=db,
        ticker=ticker,
        company_name="NVIDIA Corporation",
        filing_type=form,
        filing_date=filing_date,
        content="Second version content."
    )
    chunks_data2 = [
        {
            "document_id": doc2.id,
            "chunk_index": 0,
            "chunk_text": "Second version content.",
            "embedding": [0.0] * 384,
            "chunk_metadata": {"ticker": ticker}
        }
    ]
    documents.create_document_chunks_bulk(db, chunks_data2)
    
    # Verify second version is stored successfully
    stored_doc = documents.get_document(db, doc2.id)
    assert stored_doc is not None
    assert stored_doc.content == "Second version content."
    assert len(documents.get_chunks_by_document(db, doc2.id)) == 1
