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
- **Phase 7 (Retrieval)**: Implemented hybrid search retrieval layer combining pgvector cosine distance semantic search, full-text search (tsvector @@ plainto_tsquery) lexical search, and Reciprocal Rank Fusion (RRF) rank aggregation (with k = 60).

- **Phase 8 (Agent)**: Wired up the retrieved context to a PydanticAI agent utilizing Groq (`llama-3.3-70b-versatile`) to generate grounded, structured responses.
- **Phase 9 (Citations)**: Implemented citation validation layer (`validate_grounding`) checking chunk IDs, document IDs, and verifying normalized excerpts as substrings.
- **Phase 10 (Streaming)**: Implemented server-sent events (SSE) chat streaming route (`POST /chat/stream`) sending text-deltas, real-time citations, complete message payloads, and errors. Integrated client-side SSE reader in `useMessages.ts` to render streaming responses incrementally in the UI.

## Active Phase (Where we left off)
- Finished **Phase 11 (Polish)**. The visual layout, premium transitions, interactive elements, glassmorphic overlays, and brand-matching citations are complete. Next.js production builds compile successfully.

## Next Immediate Steps
1. **Phase 12 (Deployment)**: Configure Railway deployment setups for the frontend and backend, configure production credentials/Supabase database connections, and run the final verification test suite.

