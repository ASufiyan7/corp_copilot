import pytest
import uuid
from pydantic_ai.models.test import TestModel
from app.llm.factory import llm_factory
from pydantic_ai.models.groq import GroqModel
from app.assistant.outputs import GroundedAnswer, Citation
from app.assistant.deps import AgentDeps
from app.assistant.agent import agent, generate_dynamic_prompt
from app.database.models import DocumentChunk, SourceDocument

def test_llm_factory():
    # Verify factory constructs the correct Model subtypes
    groq_model = llm_factory.create("groq", "llama-3.3-70b-versatile")
    assert isinstance(groq_model, GroqModel)
    assert groq_model.model_name == "llama-3.3-70b-versatile"

    with pytest.raises(ValueError):
        llm_factory.create("invalid_provider_xyz", "some-model")

def test_dynamic_system_prompt():
    # Create mock chunks
    doc = SourceDocument(id=uuid.uuid4(), ticker="AAPL", filing_type="10-K")
    chunk_1 = DocumentChunk(
        id=uuid.uuid4(),
        document_id=doc.id,
        chunk_text="Apple iPhone 15 sales rose.",
        document=doc
    )
    chunk_2 = DocumentChunk(
        id=uuid.uuid4(),
        document_id=doc.id,
        chunk_text="Services margin expanded to 70%.",
        document=doc
    )

    deps = AgentDeps(retrieved_chunks=[chunk_1, chunk_2])
    
    # Build a mock RunContext to pass to the dynamic system prompt function
    class MockRunContext:
        def __init__(self, deps):
            self.deps = deps
            
    ctx = MockRunContext(deps)
    system_prompt = generate_dynamic_prompt(ctx)
    
    assert "Apple iPhone 15 sales rose." in system_prompt
    assert "Services margin expanded to 70%." in system_prompt
    assert str(chunk_1.id) in system_prompt
    assert str(chunk_2.id) in system_prompt
    assert "AAPL" in system_prompt
    assert "10-K" in system_prompt
    assert "Grounding Rules" in system_prompt

@pytest.mark.anyio
async def test_agent_execution_with_test_model():
    # Set up mock dependency chunks
    doc_id = uuid.uuid4()
    chunk_id = uuid.uuid4()
    doc = SourceDocument(id=doc_id, ticker="NVDA", filing_type="10-K")
    chunk = DocumentChunk(
        id=chunk_id,
        document_id=doc_id,
        chunk_text="NVIDIA AI demand is strong.",
        document=doc
    )
    
    deps = AgentDeps(retrieved_chunks=[chunk])
    
    # Use PydanticAI's TestModel to run the agent without hitting any external API.
    # TestModel will generate structural output of GroundedAnswer automatically.
    custom_args = {
        "answer": "NVIDIA AI demand is strong.",
        "citations": [
            {
                "chunk_id": str(chunk_id),
                "document_id": str(doc_id),
                "excerpt": "NVIDIA AI demand is strong."
            }
        ],
        "supporting_passages": ["NVIDIA AI demand is strong."]
    }
    test_model = TestModel(custom_output_args=custom_args)
    
    result = await agent.run(
        "What is the AI demand?",
        deps=deps,
        model=test_model
    )
    
    assert isinstance(result.output, GroundedAnswer)
    assert result.output.answer == "NVIDIA AI demand is strong."
    assert len(result.output.citations) == 1
    assert result.output.citations[0].chunk_id == chunk_id
    assert result.output.citations[0].document_id == doc_id
    assert result.output.citations[0].excerpt == "NVIDIA AI demand is strong."
    assert result.output.supporting_passages == ["NVIDIA AI demand is strong."]
