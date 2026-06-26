import pytest
import uuid
from app.database.models import DocumentChunk
from app.assistant.outputs import GroundedAnswer, Citation
from app.grounding import validate_grounding, GroundingValidationError

@pytest.fixture
def sample_chunks():
    doc1_id = uuid.uuid4()
    doc2_id = uuid.uuid4()
    
    chunk1 = DocumentChunk(
        id=uuid.uuid4(),
        document_id=doc1_id,
        chunk_text="Apple services margins grew dramatically to 70.5% in early 2024.\nThis represents an all-time record high segment performance."
    )
    chunk2 = DocumentChunk(
        id=uuid.uuid4(),
        document_id=doc2_id,
        chunk_text="NVIDIA GPU supply constraints were discussed at length by executive management. Data center segment continues capacity expansion."
    )
    return [chunk1, chunk2]

def test_validate_grounding_success(sample_chunks):
    # Valid GroundedAnswer
    c1 = sample_chunks[0]
    c2 = sample_chunks[1]
    
    answer = GroundedAnswer(
        answer="Apple services margins grew to 70.5% and NVIDIA has supply constraints.",
        citations=[
            Citation(chunk_id=c1.id, document_id=c1.document_id, excerpt="Apple services margins grew dramatically to 70.5%"),
            Citation(chunk_id=c2.id, document_id=c2.document_id, excerpt="NVIDIA GPU supply constraints were discussed")
        ],
        supporting_passages=[
            "Apple services margins grew dramatically to 70.5%",
            "NVIDIA GPU supply constraints were discussed"
        ]
    )
    
    # Should not raise any exception
    validate_grounding(answer, sample_chunks)

def test_validate_grounding_invalid_chunk_id(sample_chunks):
    c1 = sample_chunks[0]
    fake_chunk_id = uuid.uuid4()
    
    answer = GroundedAnswer(
        answer="Some answer",
        citations=[
            Citation(chunk_id=fake_chunk_id, document_id=c1.document_id, excerpt="Apple services margins")
        ],
        supporting_passages=["Apple services margins"]
    )
    
    with pytest.raises(GroundingValidationError) as exc_info:
        validate_grounding(answer, sample_chunks)
    assert "was not in the retrieved context" in str(exc_info.value)

def test_validate_grounding_invalid_document_id(sample_chunks):
    c1 = sample_chunks[0]
    fake_doc_id = uuid.uuid4()
    
    answer = GroundedAnswer(
        answer="Some answer",
        citations=[
            Citation(chunk_id=c1.id, document_id=fake_doc_id, excerpt="Apple services margins")
        ],
        supporting_passages=["Apple services margins"]
    )
    
    with pytest.raises(GroundingValidationError) as exc_info:
        validate_grounding(answer, sample_chunks)
    assert "does not match the retrieved chunk's document_id" in str(exc_info.value)

def test_validate_grounding_empty_excerpt(sample_chunks):
    c1 = sample_chunks[0]
    
    answer = GroundedAnswer(
        answer="Some answer",
        citations=[
            Citation(chunk_id=c1.id, document_id=c1.document_id, excerpt=" ")
        ],
        supporting_passages=[" "]
    )
    
    with pytest.raises(GroundingValidationError) as exc_info:
        validate_grounding(answer, sample_chunks)
    assert "excerpt is empty" in str(exc_info.value)

def test_validate_grounding_fabricated_excerpt(sample_chunks):
    c1 = sample_chunks[0]
    
    answer = GroundedAnswer(
        answer="Some answer",
        citations=[
            Citation(chunk_id=c1.id, document_id=c1.document_id, excerpt="Apple services margins grew to 95%")
        ],
        supporting_passages=["Apple services margins grew to 95%"]
    )
    
    with pytest.raises(GroundingValidationError) as exc_info:
        validate_grounding(answer, sample_chunks)
    assert "excerpt is not a substring of the source chunk text" in str(exc_info.value)

def test_validate_grounding_whitespace_normalization(sample_chunks):
    c1 = sample_chunks[0]
    
    # Excerpt has clean single spacing, whereas c1.chunk_text has newlines and extra spaces
    excerpt_with_newline = "Apple services margins grew dramatically to 70.5% in early 2024."
    
    answer = GroundedAnswer(
        answer="Margins grew",
        citations=[
            Citation(chunk_id=c1.id, document_id=c1.document_id, excerpt=excerpt_with_newline)
        ],
        supporting_passages=[excerpt_with_newline]
    )
    
    # Should pass successfully because of whitespace normalization
    validate_grounding(answer, sample_chunks)
