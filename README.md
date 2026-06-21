# Document Copilot

Document Copilot is a production-style AI research assistant that allows users to query a curated SEC filing corpus using natural language and receive grounded, citable answers.

The project is designed to demonstrate modern AI engineering practices including:

- Retrieval-Augmented Generation (RAG)
- Hybrid search (semantic + keyword)
- Citation enforcement
- Grounding validation
- Streaming AI responses
- Authentication and user management
- Production deployment

The primary goal is trust: every answer should be traceable back to source documents.

---

# Project Overview

Analysts spend significant time reading SEC filings before they can perform meaningful analysis.

Document Copilot reduces that intake work by allowing users to:

- Ask questions in plain English
- Search across SEC filings
- Compare companies across years
- Review supporting passages
- Verify every factual claim through citations

Example questions:

- How did NVIDIA describe AI demand between 2021 and 2025?
- How did AWS profitability compare to Amazon's retail business?
- What changed in Microsoft's discussion of cloud infrastructure over time?
- Which companies materially changed AI-related risk disclosures?

---

# Key Features

## Grounded Answers

Answers are generated only from retrieved source passages.

## Citations

Every factual claim must be backed by source evidence.

## Hybrid Retrieval

Combines:

- Semantic search using pgvector
- Postgres full-text search
- Reciprocal Rank Fusion (RRF)

## Conversation History

Users can revisit previous conversations.

## Authentication

Supabase email authentication.

## Streaming Responses

Answers stream incrementally to the UI.

---

# Architecture

```text
React SPA
    │
    ▼
FastAPI Backend
    │
    ▼
PydanticAI Agent
    │
    ▼
Groq (Llama 3.3 70B)
    │
    ▼
Grounded Response

Retrieval Layer
    ├─ pgvector Search
    ├─ Full Text Search
    └─ RRF Fusion

Storage
    └─ Supabase Postgres
```

For full details see:

```text
docs/architecture.md
```

---

# Tech Stack

| Layer | Technology |
|---------|---------|
| Frontend | React + Vite + TypeScript |
| UI | Tailwind CSS + shadcn/ui |
| Backend | FastAPI |
| Agent Framework | PydanticAI |
| LLM | Groq |
| Model | llama-3.3-70b-versatile |
| Embeddings | BAAI/bge-small-en-v1.5 |
| Database | Supabase Postgres |
| Vector Search | pgvector |
| Search | PostgreSQL Full Text Search |
| Auth | Supabase Auth |
| Deployment | Railway |

---

# Repository Structure

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

# Prerequisites

Install:

- Python 3.12+
- uv
- Node.js 20+
- pnpm

---

# Environment Variables

## Backend

```env
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

DATABASE_URL=

GROQ_API_KEY=

LLM_PROVIDER=groq
MODEL_NAME=llama-3.3-70b-versatile

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSIONS=384

ALLOWED_ORIGINS=
```

## Frontend

```env
VITE_API_BASE_URL=
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

---

# Local Development

Backend:

```bash
cd backend

uv sync

uv run uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend

pnpm install

pnpm dev
```

---

# Sample Data

The repository includes a downloader for SEC filings.

Example companies:

- Apple
- Microsoft
- NVIDIA
- Amazon
- Alphabet

The ingestion pipeline:

1. Downloads filings
2. Normalizes content
3. Chunks documents
4. Generates embeddings
5. Stores vectors in Supabase

---

# Design Principles

## Retrieval First

Documents are retrieved before generation.

## Provider Agnostic

The system supports multiple LLM providers through a shared interface.

Current default:

```env
LLM_PROVIDER=groq
```

Future providers:

- OpenAI
- Anthropic
- OpenRouter

## Low Cost

Embeddings are generated locally using Sentence Transformers.

## Trust Over Creativity

The system prioritizes factual accuracy and citation quality over open-ended generation.

---

# Deployment

Frontend:

- Railway

Backend:

- Railway

Database:

- Supabase

The backend remains stateless and all persistent data lives in Supabase.

---

# Portfolio Goals

This project demonstrates:

- Full-stack development
- AI application architecture
- Retrieval-Augmented Generation
- Vector databases
- Authentication
- Streaming APIs
- Deployment workflows
- Grounding and citation systems

---

# Non-Goals

- Stock recommendations
- Trading advice
- External news data
- Social media analysis
- Multi-tenant SaaS

---

# License

For educational and portfolio purposes.
