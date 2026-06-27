import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.database import chats
from app.database.models import Profile

router = APIRouter(prefix="/threads", tags=["threads"])

# --- Pydantic Models ---

class ThreadResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ThreadCreate(BaseModel):
    id: Optional[uuid.UUID] = None
    title: Optional[str] = "New Research Chat"

class ThreadUpdate(BaseModel):
    title: str

class CitationResponse(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    excerpt: str
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    filing_type: Optional[str] = None
    filing_date: Optional[str] = None

class MessageResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    citations: Optional[List[CitationResponse]] = None

    model_config = ConfigDict(from_attributes=True)

# --- Routes ---

@router.get("", response_model=List[ThreadResponse])
async def list_threads(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all threads for the authenticated user, sorted by updated_at descending.
    """
    return chats.get_threads_by_user(db, current_user.id)

@router.post("", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    payload: ThreadCreate,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new thread for the authenticated user.
    If an id is provided in the payload, use it if it does not already exist.
    """
    if payload.id:
        existing = chats.get_thread(db, payload.id)
        if existing:
            if existing.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Thread ID already exists and belongs to another user"
                )
            return existing

    thread = chats.create_thread(
        db,
        user_id=current_user.id,
        title=payload.title,
        thread_id=payload.id
    )
    return thread

@router.get("/{thread_id}", response_model=List[MessageResponse])
async def get_thread_messages(
    thread_id: uuid.UUID,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all messages in a specific thread, including citations for assistant messages.
    """
    thread = chats.get_thread(db, thread_id)
    if not thread or thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    messages = chats.get_messages_by_thread(db, thread_id)
    response = []
    
    for msg in messages:
        citations = []
        if msg.role == "assistant":
            citations_db = chats.get_citations_by_message(db, msg.id)
            for cit in citations_db:
                chunk = cit.chunk
                doc = chunk.document if chunk else None
                citations.append(
                    CitationResponse(
                        chunk_id=cit.chunk_id,
                        document_id=chunk.document_id if chunk else uuid.UUID(int=0),
                        excerpt=chunk.chunk_text if chunk else "",
                        ticker=doc.ticker if doc else None,
                        company_name=doc.company_name if doc else None,
                        filing_type=doc.filing_type if doc else None,
                        filing_date=doc.filing_date.isoformat() if doc and doc.filing_date else None,
                    )
                )

        response.append(
            MessageResponse(
                id=msg.id,
                thread_id=msg.thread_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                citations=citations if msg.role == "assistant" else None
            )
        )

    return response

@router.patch("/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: uuid.UUID,
    payload: ThreadUpdate,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the title of a specific thread.
    """
    thread = chats.get_thread(db, thread_id)
    if not thread or thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    updated = chats.update_thread_title(db, thread_id, payload.title)
    return updated

@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
    thread_id: uuid.UUID,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific thread and its associated messages/citations.
    """
    thread = chats.get_thread(db, thread_id)
    if not thread or thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    chats.delete_thread(db, thread_id)
    return
