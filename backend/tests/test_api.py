import pytest
import uuid
import json
from datetime import date, datetime
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.database.session import get_db
from app.database import chats, documents
from app.database.models import Profile, ChatThread, ChatMessage, MessageCitation
from app.assistant.outputs import GroundedAnswer, Citation
from tests.test_database import db, engine

client = TestClient(app)

@pytest.fixture
def test_user(db):
    """Create a test user and sync to local profiles."""
    user_id = uuid.uuid4()
    email = "test_analyst@driftwood.com"
    profile = chats.create_profile(db, email=email, profile_id=user_id)
    return profile

@pytest.fixture
def mock_auth(test_user):
    """Mock the authentication to return our test user."""
    mock_res = MagicMock()
    mock_res.user = MagicMock(id=str(test_user.id), email=test_user.email)
    
    with patch("app.auth.dependencies.supabase_client.auth.get_user", return_value=mock_res) as mock:
        yield test_user

@pytest.fixture
def setup_data(db):
    """Seed test documents and chunks."""
    doc_id = uuid.uuid4()
    doc = documents.create_document(
        db,
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        filing_type="10-K",
        filing_date=date(2025, 2, 26),
        content="NVIDIA AI demand is strong.",
        source_url="https://sec.gov/nvda-10k",
        doc_id=doc_id
    )
    
    chunks_to_create = [
        {
            "document_id": doc_id,
            "chunk_index": 0,
            "chunk_text": "NVIDIA AI demand is strong in data centers.",
            "embedding": [0.1] * 384,
            "chunk_metadata": {"page": 1}
        }
    ]
    db_chunks = documents.create_document_chunks_bulk(db, chunks_to_create)
    return doc, db_chunks

class MockRunResult:
    def __init__(self, data: GroundedAnswer):
        self.data = data

class MockStreamedRunResult:
    def __init__(self, final_answer: GroundedAnswer):
        self.final_answer = final_answer

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def stream_output(self):
        yield GroundedAnswer(
            answer="NVIDIA AI ",
            citations=[],
            supporting_passages=[]
        )
        yield self.final_answer

    async def get_data(self):
        return self.final_answer

def test_thread_crud(mock_auth, db):
    app.dependency_overrides[get_db] = lambda: db
    
    try:
        # Create Thread
        headers = {"Authorization": "Bearer fake_token"}
        create_payload = {"title": "NVIDIA Analysis"}
        res = client.post("/api/threads", json=create_payload, headers=headers)
        assert res.status_code == 201
        thread_data = res.json()
        assert thread_data["title"] == "NVIDIA Analysis"
        thread_id = thread_data["id"]

        # List Threads
        res = client.get("/api/threads", headers=headers)
        assert res.status_code == 200
        threads_list = res.json()
        assert len(threads_list) >= 1
        assert any(t["id"] == thread_id for t in threads_list)

        # Update Thread Title
        update_payload = {"title": "Updated NVIDIA Analysis"}
        res = client.patch(f"/api/threads/{thread_id}", json=update_payload, headers=headers)
        assert res.status_code == 200
        assert res.json()["title"] == "Updated NVIDIA Analysis"

        # Delete Thread
        res = client.delete(f"/api/threads/{thread_id}", headers=headers)
        assert res.status_code == 204

        # Verify Deleted
        res = client.get(f"/api/threads/{thread_id}", headers=headers)
        assert res.status_code == 404
    finally:
        app.dependency_overrides.clear()

def test_chat_interaction_sync(mock_auth, setup_data, db):
    app.dependency_overrides[get_db] = lambda: db
    doc, chunks = setup_data
    
    # Create thread first
    thread = chats.create_thread(db, user_id=mock_auth.id, title="Sync Chat")
    
    # Mock retrieval and agent
    mock_grounded_answer = GroundedAnswer(
        answer="NVIDIA AI demand is strong.",
        citations=[
            Citation(
                chunk_id=chunks[0].id,
                document_id=doc.id,
                excerpt="NVIDIA AI demand is strong"  # No period to match substring in "NVIDIA AI demand is strong in data centers."
            )
        ],
        supporting_passages=["NVIDIA AI demand is strong"]
    )
    
    with patch("app.api.chat.retrieve_chunks", return_value=chunks) as mock_retrieval, \
         patch("app.api.chat.agent.run", new_callable=AsyncMock) as mock_agent_run:
         
        mock_agent_run.return_value = MockRunResult(mock_grounded_answer)
        
        headers = {"Authorization": "Bearer fake_token"}
        payload = {"threadId": str(thread.id), "message": "Is NVIDIA AI demand strong?"}
        
        res = client.post("/api/chat", json=payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["answer"] == "NVIDIA AI demand is strong."
        assert len(data["citations"]) == 1
        assert data["citations"][0]["chunk_id"] == str(chunks[0].id)
        assert data["citations"][0]["ticker"] == "NVDA"
        
        # Verify messages in DB
        msgs = chats.get_messages_by_thread(db, thread.id)
        assert len(msgs) == 2
        assert msgs[0].role == "user"
        assert msgs[1].role == "assistant"
        
        # Verify message citations in DB
        cits = chats.get_citations_by_message(db, msgs[1].id)
        assert len(cits) == 1
        assert cits[0].chunk_id == chunks[0].id
        
        # Verify GET /api/threads/{id} returns message history with citations
        res_history = client.get(f"/api/threads/{thread.id}", headers=headers)
        assert res_history.status_code == 200
        history_data = res_history.json()
        assert len(history_data) == 2
        assert history_data[1]["citations"][0]["chunk_id"] == str(chunks[0].id)
        assert history_data[1]["citations"][0]["ticker"] == "NVDA"
        
    app.dependency_overrides.clear()

def test_chat_interaction_streaming(mock_auth, setup_data, db):
    app.dependency_overrides[get_db] = lambda: db
    doc, chunks = setup_data
    
    thread = chats.create_thread(db, user_id=mock_auth.id, title="Stream Chat")
    
    mock_grounded_answer = GroundedAnswer(
        answer="NVIDIA AI demand is strong.",
        citations=[
            Citation(
                chunk_id=chunks[0].id,
                document_id=doc.id,
                excerpt="NVIDIA AI demand is strong"  # No period to match substring
            )
        ],
        supporting_passages=["NVIDIA AI demand is strong"]
    )
    
    # Protect our db instance close method from actual closure
    original_close = db.close
    db.close = MagicMock()
    
    try:
        # Patch SessionLocal to return transactional db instance to avoid ForeignKeyViolation
        with patch("app.api.chat.SessionLocal", return_value=db), \
             patch("app.api.chat.retrieve_chunks", return_value=chunks) as mock_retrieval, \
             patch("app.api.chat.agent.run_stream", return_value=MockStreamedRunResult(mock_grounded_answer)) as mock_agent_run_stream:
             
            headers = {"Authorization": "Bearer fake_token"}
            payload = {"threadId": str(thread.id), "message": "Is NVIDIA AI demand strong?"}
            
            # Call streaming endpoint
            res = client.post("/api/chat/stream", json=payload, headers=headers)
            assert res.status_code == 200
            assert "text/event-stream" in res.headers["content-type"]
            
            # Collect and parse SSE chunks
            events = []
            for line in res.iter_lines():
                if line:
                    events.append(line)
                    
            # Let's check event types yielded
            event_str = "\n".join(events)
            assert "event: text-delta" in event_str
            assert "event: citation" in event_str
            assert "event: complete" in event_str
            
            # Verify messages in DB
            msgs = chats.get_messages_by_thread(db, thread.id)
            assert len(msgs) == 2
            assert msgs[0].role == "user"
            assert msgs[1].role == "assistant"
            assert msgs[1].content == "NVIDIA AI demand is strong."
    finally:
        # Restore actual close method
        db.close = original_close
        app.dependency_overrides.clear()
