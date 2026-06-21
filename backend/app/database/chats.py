import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import Profile, ChatThread, ChatMessage, MessageCitation

# --- Profile CRUD ---

def get_profile(db: Session, profile_id: uuid.UUID) -> Optional[Profile]:
    """Retrieve a profile by its UUID."""
    return db.query(Profile).filter(Profile.id == profile_id).first()

def get_profile_by_email(db: Session, email: str) -> Optional[Profile]:
    """Retrieve a profile by email address."""
    return db.query(Profile).filter(Profile.email == email).first()

def create_profile(db: Session, email: str, profile_id: Optional[uuid.UUID] = None) -> Profile:
    """Create a new user profile."""
    new_id = profile_id or uuid.uuid4()
    db_profile = Profile(id=new_id, email=email)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

# --- ChatThread CRUD ---

def get_thread(db: Session, thread_id: uuid.UUID) -> Optional[ChatThread]:
    """Retrieve a specific chat thread by its UUID."""
    return db.query(ChatThread).filter(ChatThread.id == thread_id).first()

def get_threads_by_user(db: Session, user_id: uuid.UUID) -> List[ChatThread]:
    """Retrieve all chat threads for a user, sorted by update time descending."""
    return db.query(ChatThread).filter(ChatThread.user_id == user_id).order_by(desc(ChatThread.updated_at)).all()

def create_thread(
    db: Session, 
    user_id: uuid.UUID, 
    title: Optional[str] = None, 
    thread_id: Optional[uuid.UUID] = None
) -> ChatThread:
    """Create a new chat thread."""
    new_id = thread_id or uuid.uuid4()
    db_thread = ChatThread(id=new_id, user_id=user_id, title=title)
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    return db_thread

def update_thread_title(db: Session, thread_id: uuid.UUID, title: str) -> Optional[ChatThread]:
    """Update the title of an existing chat thread."""
    db_thread = get_thread(db, thread_id)
    if db_thread:
        db_thread.title = title
        db.commit()
        db.refresh(db_thread)
    return db_thread

def delete_thread(db: Session, thread_id: uuid.UUID) -> bool:
    """Delete a chat thread and cascade delete its messages and citations."""
    db_thread = get_thread(db, thread_id)
    if db_thread:
        db.delete(db_thread)
        db.commit()
        return True
    return False

# --- ChatMessage CRUD ---

def get_messages_by_thread(db: Session, thread_id: uuid.UUID) -> List[ChatMessage]:
    """Retrieve all messages in a chat thread, ordered by creation time ascending."""
    return db.query(ChatMessage).filter(ChatMessage.thread_id == thread_id).order_by(ChatMessage.created_at).all()

def create_message(
    db: Session, 
    thread_id: uuid.UUID, 
    role: str, 
    content: str, 
    message_id: Optional[uuid.UUID] = None
) -> ChatMessage:
    """Create a new chat message and update the thread's updated_at timestamp."""
    new_id = message_id or uuid.uuid4()
    db_message = ChatMessage(id=new_id, thread_id=thread_id, role=role, content=content)
    db.add(db_message)
    
    # Touch the parent thread to update its updated_at timestamp
    db_thread = get_thread(db, thread_id)
    if db_thread:
        db_thread.updated_at = db_message.created_at
        
    db.commit()
    db.refresh(db_message)
    return db_message

# --- MessageCitation CRUD ---

def create_citation(db: Session, message_id: uuid.UUID, chunk_id: uuid.UUID) -> MessageCitation:
    """Create a citation linking a message to a source document chunk."""
    db_citation = MessageCitation(id=uuid.uuid4(), message_id=message_id, chunk_id=chunk_id)
    db.add(db_citation)
    db.commit()
    db.refresh(db_citation)
    return db_citation

def get_citations_by_message(db: Session, message_id: uuid.UUID) -> List[MessageCitation]:
    """Retrieve all citations associated with a message."""
    return db.query(MessageCitation).filter(MessageCitation.message_id == message_id).all()
