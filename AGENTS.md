# Agent Instructions

This file is the source of truth for any coding agent (Claude Code, Cursor, Codex, OpenAI Codex, etc.) working in this repository.

Read this file before modifying code.

---

# Project Overview

Document Copilot is a production-style document intelligence platform for querying SEC filings using natural language.

Core principles:

- Retrieval before generation
- Grounded answers only
- Mandatory citations
- Provider-agnostic inference
- Low operational cost
- Simple deployment

The project is designed to demonstrate modern AI engineering patterns rather than operate as a large-scale SaaS product.

---

# Locked Stack

Unless explicitly instructed otherwise, the stack is considered fixed.

## Frontend

- React
- Vite
- TypeScript
- React Router
- Tailwind CSS
- shadcn/ui
- Supabase JS SDK

## Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- PydanticAI
- SQLAlchemy
- Alembic
- Sentence Transformers
- Groq SDK

## Database

- Supabase Postgres
- pgvector
- PostgreSQL Full Text Search

## Infrastructure

- Railway
- Supabase

---

# LLM Architecture

The project uses a provider-agnostic LLM layer.

Current provider:

```env
LLM_PROVIDER=groq
MODEL_NAME=llama-3.3-70b-versatile
```

Future providers may include:

- OpenAI
- Anthropic
- OpenRouter

Agents must never directly instantiate a provider SDK inside business logic.

Allowed:

```python
llm = llm_factory.create(settings.llm_provider)
```

Not allowed:

```python
client = Groq(...)
```

inside retrieval, orchestration, or business modules.

---

# Embeddings

Default embedding model:

```text
BAAI/bge-small-en-v1.5
```

Embeddings are generated locally through Sentence Transformers.

Do not introduce external embedding APIs without a documented reason.

---

# Repository Layout

```text
document-copilot/
├── AGENTS.md
├── README.md
├── data/
├── docs/
├── backend/
└── frontend/
```

---

# Dependency Policy

Default rule:

Write it yourself.

Only add a dependency when:

- The problem is non-trivial.
- The dependency is widely adopted.
- The dependency meaningfully reduces complexity.

Acceptable categories:

- HTTP clients
- Database drivers
- ORMs
- Migration tools
- Authentication SDKs
- LLM SDKs
- Vector search dependencies

Avoid:

- Utility wrappers
- Convenience libraries
- Tiny helper dependencies

Before adding a dependency answer:

1. What problem does it solve?
2. How often will it be used?
3. Can we implement it ourselves in under 30 lines?

If the answer to #3 is yes, do not add the dependency.

---

# Configuration Rules

Configuration must have a single source of truth.

Backend:

```text
backend/app/config.py
```

Frontend:

```text
frontend/src/lib/env.ts
```

Never:

- Read environment variables directly throughout the codebase.
- Scatter getenv calls.
- Use load_dotenv in application code.

Fail fast when configuration is missing.

---

# Code Style

## Prefer Small Functions

Good:

- Short
- Focused
- Obvious

Bad:

- Deep abstraction hierarchies
- Clever patterns
- Premature generalization

---

## Avoid Premature Abstraction

Do not create:

- Base classes
- Generic services
- Framework layers

until there is a real need.

Three duplicated lines are better than a bad abstraction.

---

## Validate at Boundaries

Validate:

- API requests
- External responses
- User input

Do not add defensive checks for internal invariants that cannot fail.

---

## Comments

Comments explain:

WHY

not

WHAT

Remove outdated comments immediately.

---

## Keep Files Focused

Prefer:

```text
retrieval/search.py
retrieval/fusion.py
retrieval/rerank.py
```

over:

```text
retrieval/everything.py
```

---

# Retrieval Rules

Hybrid retrieval is required.

Always use:

1. pgvector semantic search
2. Full-text search
3. Reciprocal Rank Fusion

Do not replace retrieval with:

- Agent-generated SQL
- Full corpus prompting
- Naive keyword matching

---

# Grounding Rules

Grounding is a system guarantee.

The assistant must:

- Answer only from retrieved evidence.
- Cite every factual claim.
- Refuse unsupported conclusions.
- Never fabricate citations.

If citation validation fails:

- Reject the response.
- Surface a controlled error.

Never silently continue.

---

# Frontend Rules

Frontend responsibilities:

- Authentication
- Chat rendering
- Streaming display
- Citation display
- User interaction

Frontend must not:

- Call LLM providers directly.
- Perform retrieval.
- Access privileged Supabase credentials.

---

# Backend Rules

Backend responsibilities:

- Authentication verification
- Retrieval
- Prompt construction
- Agent execution
- Citation validation
- Persistence

The backend is the source of truth.

---

# Database Rules

Store:

- Users
- Threads
- Messages
- Documents
- Chunks
- Citations

Use pgvector for semantic retrieval.

Use PostgreSQL full-text search for lexical retrieval.

Do not introduce a separate vector database.

---

# Deployment Rules

Target deployment:

Frontend:
- Railway

Backend:
- Railway

Database:
- Supabase

Keep services stateless whenever possible.

Persistent state belongs in Supabase.

---

# Success Criteria

A user should be able to:

1. Sign up.
2. Log in.
3. Ask a question about SEC filings.
4. Receive a grounded answer.
5. Verify citations.
6. Inspect supporting passages.

Trust and traceability are more important than creativity.
