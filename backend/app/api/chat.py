import uuid
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db, SessionLocal
from app.database import chats
from app.database.models import Profile
from app.retrieval.retriever import retrieve_chunks
from app.assistant.agent import agent
from app.assistant.deps import AgentDeps
from app.grounding.validator import validate_grounding, GroundingValidationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# --- Pydantic Models ---

class ChatRequest(BaseModel):
    threadId: uuid.UUID
    message: str

class CitationResponse(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    excerpt: str
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    filing_type: Optional[str] = None
    filing_date: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationResponse]

# --- SSE Helper Generator ---

async def event_generator(thread_id: uuid.UUID, message_content: str, user_id: uuid.UUID):
    """
    Background generator for streaming chat response updates using Server-Sent Events (SSE).
    Uses its own database session to ensure it remains open during asynchronous streaming.
    """
    db = SessionLocal()
    try:
        # 1. Create and persist user message
        chats.create_message(db, thread_id=thread_id, role="user", content=message_content)

        # 2. Retrieve context chunks using hybrid search
        retrieved_chunks = retrieve_chunks(db, query=message_content, limit=10)

        # 3. Stream from PydanticAI agent
        deps = AgentDeps(retrieved_chunks=retrieved_chunks)
        last_answer = ""
        sent_citations = set()

        async with agent.run_stream(message_content, deps=deps) as result:
            async for current_ans in result.stream_output():
                # Send text increments
                new_text = current_ans.answer[len(last_answer):]
                if new_text:
                    yield f"event: text-delta\ndata: {json.dumps({'delta': new_text})}\n\n"
                    last_answer = current_ans.answer

                # Send citations as they are parsed
                for citation in current_ans.citations:
                    if citation.chunk_id not in sent_citations:
                        chunk_map = {chunk.id: chunk for chunk in retrieved_chunks}
                        if citation.chunk_id in chunk_map:
                            chunk = chunk_map[citation.chunk_id]
                            doc = chunk.document
                            citation_data = {
                                "chunk_id": str(citation.chunk_id),
                                "document_id": str(citation.document_id),
                                "excerpt": citation.excerpt,
                                "ticker": doc.ticker if doc else None,
                                "company_name": doc.company_name if doc else None,
                                "filing_type": doc.filing_type if doc else None,
                                "filing_date": doc.filing_date.isoformat() if doc and doc.filing_date else None,
                            }
                            yield f"event: citation\ndata: {json.dumps(citation_data)}\n\n"
                            sent_citations.add(citation.chunk_id)

            # Send final remainder text if any
            final_answer = await result.get_data()
            new_text = final_answer.answer[len(last_answer):]
            if new_text:
                yield f"event: text-delta\ndata: {json.dumps({'delta': new_text})}\n\n"

            # Send final citations if any were skipped
            for citation in final_answer.citations:
                if citation.chunk_id not in sent_citations:
                    chunk_map = {chunk.id: chunk for chunk in retrieved_chunks}
                    if citation.chunk_id in chunk_map:
                        chunk = chunk_map[citation.chunk_id]
                        doc = chunk.document
                        citation_data = {
                            "chunk_id": str(citation.chunk_id),
                            "document_id": str(citation.document_id),
                            "excerpt": citation.excerpt,
                            "ticker": doc.ticker if doc else None,
                            "company_name": doc.company_name if doc else None,
                            "filing_type": doc.filing_type if doc else None,
                            "filing_date": doc.filing_date.isoformat() if doc and doc.filing_date else None,
                        }
                        yield f"event: citation\ndata: {json.dumps(citation_data)}\n\n"
                        sent_citations.add(citation.chunk_id)

        # 4. Enforce Grounding and citation validation on the final completed structure
        try:
            validate_grounding(final_answer, retrieved_chunks)
        except GroundingValidationError as validation_err:
            logger.warning(f"Grounding validation failed: {str(validation_err)}")
            yield f"event: error\ndata: {json.dumps({'detail': str(validation_err)})}\n\n"
            return

        # 5. Persist assistant message and citations in the database
        asst_msg = chats.create_message(db, thread_id=thread_id, role="assistant", content=final_answer.answer)
        for citation in final_answer.citations:
            chats.create_citation(db, message_id=asst_msg.id, chunk_id=citation.chunk_id)

        # 6. Construct complete message payload with resolved documents
        response_citations = []
        chunk_map = {chunk.id: chunk for chunk in retrieved_chunks}
        for citation in final_answer.citations:
            if citation.chunk_id in chunk_map:
                chunk = chunk_map[citation.chunk_id]
                doc = chunk.document
                response_citations.append({
                    "chunk_id": str(citation.chunk_id),
                    "document_id": str(citation.document_id),
                    "excerpt": citation.excerpt,
                    "ticker": doc.ticker if doc else None,
                    "company_name": doc.company_name if doc else None,
                    "filing_type": doc.filing_type if doc else None,
                    "filing_date": doc.filing_date.isoformat() if doc and doc.filing_date else None,
                })

        complete_payload = {
            "id": str(asst_msg.id),
            "thread_id": str(thread_id),
            "role": "assistant",
            "content": final_answer.answer,
            "created_at": asst_msg.created_at.isoformat(),
            "citations": response_citations
        }
        yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"

    except Exception as e:
        logger.exception("Uncaught error during SSE chat session stream")
        yield f"event: error\ndata: {json.dumps({'detail': f'Error streaming response: {str(e)}'})}\n\n"
    finally:
        db.close()

# --- Routes ---

@router.post("", response_model=ChatResponse)
async def chat_interaction(
    payload: ChatRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Standard synchronous chat endpoint.
    Retrieves context, invokes the agent, validates citations, and persists user/assistant message turns.
    """
    # Verify thread exists and belongs to the current user
    thread = chats.get_thread(db, payload.threadId)
    if not thread or thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    # 1. Save user query in the database
    chats.create_message(db, thread_id=payload.threadId, role="user", content=payload.message)

    # 2. Perform hybrid retrieval
    retrieved_chunks = retrieve_chunks(db, query=payload.message, limit=10)

    # 3. Invoke PydanticAI agent
    deps = AgentDeps(retrieved_chunks=retrieved_chunks)
    try:
        result = await agent.run(payload.message, deps=deps)
        grounded_answer = result.data
    except Exception as e:
        logger.exception("Error executing agent")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

    # 4. Perform citation grounding validation
    try:
        validate_grounding(grounded_answer, retrieved_chunks)
    except GroundingValidationError as validation_err:
        logger.warning(f"Grounding validation failed: {str(validation_err)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(validation_err)
        )

    # 5. Persist assistant message and citations
    asst_msg = chats.create_message(db, thread_id=payload.threadId, role="assistant", content=grounded_answer.answer)
    for citation in grounded_answer.citations:
        chats.create_citation(db, message_id=asst_msg.id, chunk_id=citation.chunk_id)

    # 6. Map documents and return output
    response_citations = []
    chunk_map = {chunk.id: chunk for chunk in retrieved_chunks}
    for citation in grounded_answer.citations:
        if citation.chunk_id in chunk_map:
            chunk = chunk_map[citation.chunk_id]
            doc = chunk.document
            response_citations.append(
                CitationResponse(
                    chunk_id=citation.chunk_id,
                    document_id=citation.document_id,
                    excerpt=citation.excerpt,
                    ticker=doc.ticker if doc else None,
                    company_name=doc.company_name if doc else None,
                    filing_type=doc.filing_type if doc else None,
                    filing_date=doc.filing_date.isoformat() if doc and doc.filing_date else None,
                )
            )

    return ChatResponse(
        answer=grounded_answer.answer,
        citations=response_citations
    )

@router.post("/stream")
async def chat_stream_interaction(
    payload: ChatRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SSE chat streaming route.
    Verifies ownership immediately before starting the asynchronous background streaming job.
    """
    # Verify thread exists and belongs to the current user
    thread = chats.get_thread(db, payload.threadId)
    if not thread or thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }

    return StreamingResponse(
        event_generator(payload.threadId, payload.message, current_user.id),
        media_type="text/event-stream",
        headers=headers
    )
