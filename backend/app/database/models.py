import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Date, Computed, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, relationship
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    threads = relationship("ChatThread", back_populates="user", cascade="all, delete-orphan")

class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("Profile", back_populates="threads")
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    thread = relationship("ChatThread", back_populates="messages")
    citations = relationship("MessageCitation", back_populates="message", cascade="all, delete-orphan")

class MessageCitation(Base):
    __tablename__ = "message_citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    message = relationship("ChatMessage", back_populates="citations")
    chunk = relationship("DocumentChunk")

class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String, nullable=False, index=True)
    company_name = Column(String, nullable=False)
    filing_type = Column(String, nullable=False, index=True)  # e.g., '10-K', '10-Q'
    filing_date = Column(Date, nullable=False)
    source_url = Column(String, nullable=True)
    content = Column(Text, nullable=False)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    chunk_metadata = Column("metadata", JSONB, nullable=False, server_default="{}")
    
    # Generated full text search vector column
    tsvector = Column(
        TSVECTOR,
        Computed("to_tsvector('english', chunk_text)", persisted=True),
        nullable=False
    )

    # Relationships
    document = relationship("SourceDocument", back_populates="chunks")

# Indexes
Index("idx_document_chunks_tsvector", DocumentChunk.tsvector, postgresql_using="gin")
Index(
    "idx_document_chunks_embedding",
    DocumentChunk.embedding,
    postgresql_using="hnsw",
    postgresql_ops={"embedding": "vector_cosine_ops"}
)
