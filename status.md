## Project Context
Building a production-style document intelligence platform (Document Copilot) for querying SEC filings using natural language.

## Current State & Done
- **Phase 0 (Foundation)**: Scaffolded backend (FastAPI) and frontend (React + Vite).
- **Phase 1 (Authentication)**: Configured Supabase Auth and JWT session verification on the backend.
- **Phase 2 (Database)**: Applied SQLAlchemy models and database migrations. Disabled prepared statements to allow safe transactions through Supabase's PgBouncer pooler.
- **Phase 3 (Chat UI)**: Implemented React components for sidebar threads list, chat bubble renderer, and input box.
- **Phase 4 (Chat API)**: Created API routes to create threads, retrieve message history, and persist user/assistant turns.
- **Phase 5 (Ingestion)**: Built a custom HTML text extractor and character-based sliding window chunker (1000–1200 characters with 150–200 character overlap).
- **Phase 6 (Embeddings)**: Integrated `sentence-transformers` running the BAAI/bge-small-en-v1.5 model locally on CPU. Re-ran the pipeline to fully ingest all 25 filings (Apple, Microsoft, NVIDIA, Amazon, Alphabet) with real 384-dimensional vector embeddings in Supabase Postgres.

## Active Phase (Where we left off)
- Finished **Phase 6 (Embeddings)**. All 14 automated tests (covering authentication, database CRUD operations, text chunking, and embedding generation) pass successfully.

## Next Immediate Steps
1. **Phase 7 (Retrieval)**: Implement the hybrid search retrieval layer in the backend:
   - pgvector cosine distance semantic search.
   - PostgreSQL text search index (`tsvector` @@ `tsquery`) lexical search.
   - Reciprocal Rank Fusion (RRF) rank aggregation.
2. **Phase 8 (Agent)**: Wire up the retrieved context to a PydanticAI agent utilizing Groq (`llama-3.3-70b-versatile`) to generate responses.
