# Build Specification v1 (Agent Grade)
# Document Copilot

Version: 2.0
Status: Source of Truth for Antigravity / Claude Code / Cursor Agents

---

# AGENT EXECUTION CONTRACT

You MUST:

- Read AGENTS.md
- Read architecture.md
- Read build-spec-v2.md

before making changes.

Build ONLY one phase at a time.

When a phase completes:

1. Verify acceptance criteria.
2. Run tests.
3. Summarize files changed.
4. Explain architecture decisions.
5. STOP.

Wait for human approval.

Never continue into the next phase.

---

# PRODUCT SUMMARY

Document Copilot is a production-style SEC Filing Research Assistant.

Purpose:

Help analysts search SEC filings and receive grounded answers with citations.

The system is NOT:

- A general chatbot
- An investment advisor
- A stock picker

The system IS:

- A retrieval-first research assistant
- A citation-driven RAG application
- A document intelligence platform

---

# SYSTEM ARCHITECTURE

User
→ React SPA
→ FastAPI Backend
→ Retrieval Layer
→ PydanticAI Agent
→ Groq
→ Grounded Response

Data Flow:

SEC Filing
→ Parser
→ Chunker
→ Embedding Generator
→ pgvector

Query
→ Retrieval
→ RRF Fusion
→ Context Assembly
→ LLM
→ Citation Validation
→ User

---

# TARGET REPOSITORY STRUCTURE

document-copilot/

backend/
    app/
        api/
        auth/
        assistant/
        retrieval/
        grounding/
        ingestion/
        llm/
        database/
        config.py
        main.py

frontend/
    src/
        app/
        pages/
        components/
        hooks/
        lib/
        types/

docs/
    architecture.md
    build-spec-v2.md

data/
    downloads/
    scripts/

---

# FRONTEND STRUCTURE

src/

app/
    router.tsx

pages/
    LoginPage.tsx
    ChatPage.tsx

components/
    chat/
        ChatWindow.tsx
        MessageBubble.tsx
        CitationCard.tsx
        ChatInput.tsx

    sidebar/
        ThreadList.tsx

hooks/
    useAuth.ts
    useThreads.ts
    useMessages.ts

lib/
    env.ts
    api.ts
    supabase.ts

---

# BACKEND STRUCTURE

app/

api/
    auth.py
    chat.py
    threads.py

assistant/
    agent.py
    deps.py
    outputs.py

retrieval/
    vector_search.py
    text_search.py
    fusion.py
    retriever.py

grounding/
    validator.py

llm/
    base.py
    factory.py
    providers/
        groq.py
        openai.py
        anthropic.py
        openrouter.py

database/
    models.py
    session.py
    chats.py
    documents.py

---

# DATABASE SCHEMA

profiles

id UUID PK
email TEXT
created_at TIMESTAMP

chat_threads

id UUID PK
user_id UUID
title TEXT
created_at TIMESTAMP
updated_at TIMESTAMP

chat_messages

id UUID PK
thread_id UUID
role TEXT
content TEXT
created_at TIMESTAMP

message_citations

id UUID PK
message_id UUID
chunk_id UUID

source_documents

id UUID PK
ticker TEXT
company_name TEXT
filing_type TEXT
filing_date DATE
source_url TEXT
content TEXT

document_chunks

id UUID PK
document_id UUID
chunk_index INTEGER
chunk_text TEXT
embedding VECTOR(384)
metadata JSONB

---

# PYDANTIC MODELS

ChatRequest

thread_id
message

ChatResponse

answer
citations

Citation

chunk_id
document_id
excerpt

GroundedAnswer

answer
citations
supporting_passages

---

# AUTH FLOW

Frontend:

Login
→ Supabase
→ JWT

JWT
→ FastAPI

FastAPI:

Verify Token
→ Resolve User
→ Continue Request

Reject invalid tokens immediately.

---

# INGESTION PIPELINE

Input:

Raw SEC Filing

Steps:

1. Download
2. Parse
3. Normalize
4. Chunk
5. Generate Embeddings
6. Store in Supabase

Chunk Size:

1000–1200 characters

Overlap:

150–200 characters

---

# EMBEDDING SERVICE

Model:

BAAI/bge-small-en-v1.5

Interface:

embed_text(text)

Returns:

384 dimensional vector

Generated locally.

Never call external embedding APIs.

---

# RETRIEVAL SERVICE

Step 1

Semantic Search

Top K = 20

Step 2

Full Text Search

Top K = 20

Step 3

Reciprocal Rank Fusion

Step 4

Return Top 10 Chunks

---

# RRF FORMULA

score += 1 / (k + rank)

Use:

k = 60

---

# LLM PROVIDER CONTRACT

Interface:

generate(prompt)

Providers:

Groq
OpenAI
Anthropic
OpenRouter

Default:

LLM_PROVIDER=groq

MODEL_NAME=llama-3.3-70b-versatile

---

# PYDANTIC AI AGENT

Responsibilities:

- Receive user question
- Receive retrieved context
- Generate answer
- Return structured output

Never:

- Query database directly
- Create citations itself
- Access Supabase directly

---

# GROUNDING VALIDATION

Every citation:

Must map to retrieved chunk.

If invalid:

Reject response.

Return controlled error.

No silent failures.

---

# API CONTRACTS

POST /chat

Request

{
  "threadId": "uuid",
  "message": "question"
}

Response

{
  "answer": "...",
  "citations": []
}

---

GET /threads

Returns:

[]

---

GET /threads/{id}

Returns:

messages

---

# STREAMING CONTRACT

Endpoint:

POST /chat/stream

Events:

text-delta

citation

complete

error

Frontend must render incrementally.

---

# PHASE PLAN

PHASE 0

Foundation

Acceptance:

Frontend runs.

Backend runs.

---

PHASE 1

Authentication

Acceptance:

Login works.

---

PHASE 2

Database

Acceptance:

Migration successful.

---

PHASE 3

Chat UI

Acceptance:

Threads render.

---

PHASE 4

Chat API

Acceptance:

Messages persist.

---

PHASE 5

Ingestion

Acceptance:

Filing stored.

---

PHASE 6

Embeddings

Acceptance:

Vectors generated.

---

PHASE 7

Retrieval

Acceptance:

Relevant chunks returned.

---

PHASE 8

Agent

Acceptance:

Question produces answer.

---

PHASE 9

Citations

Acceptance:

Sources visible.

---

PHASE 10

Streaming

Acceptance:

Live response rendering.

---

PHASE 11

Polish

Acceptance:

Production-quality UX.

---

PHASE 12

Deployment

Acceptance:

Publicly accessible demo.

---

# TESTING REQUIREMENTS

Each phase requires:

Unit Tests

Integration Tests

Manual Verification

No phase is complete without passing tests.

---

# FINAL DEMO TEST

Question:

How did NVIDIA describe AI demand from 2021 to 2025?

Expected:

1. Retrieval occurs.
2. Context assembled.
3. Groq generates answer.
4. Citations displayed.
5. User can inspect evidence.

Only then is the project considered complete.
