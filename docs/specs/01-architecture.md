# Architecture

## Components

```
┌─────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Frontend    │ HTTP │  FastAPI backend │      │   Ollama         │
│  (React/TS)  │◄────►│  (ragapp.api)    │◄────►│   (local LLM)    │
└─────────────┘      └────────┬─────────┘      └──────────────────┘
                               │
                      ┌────────▼─────────┐
                      │ Postgres+pgvector│
                      │ (chunks + embeds)│
                      └──────────────────┘
                               ▲
                      ┌────────┴─────────┐
                      │  Ingestion CLI    │
                      │  (PDF → chunks →  │
                      │   embeddings)     │
                      └──────────────────┘
```

## Data flow — ingestion

1. `ragapp.cli ingest <path.pdf>` loads a PDF (`ingestion/pdf_loader.py`).
2. Text is extracted per-page, then split into overlapping chunks
   (`ingestion/chunker.py`) — chunk size/overlap configurable.
3. Each chunk is embedded via a local embedding model (`ingestion/embedder.py`).
4. Chunk text + embedding + metadata (source filename, page number, chunk index)
   is upserted into Postgres (`retrieval/store.py`).

## Data flow — chat/query

1. Frontend sends a user question to `POST /api/chat`.
2. Backend embeds the question, does a similarity search against pgvector
   (`retrieval/retriever.py`) to get top-k relevant chunks, with embed/search
   timed separately (`Retriever.retrieve_with_timing`).
3. Backend builds a prompt (system instructions + retrieved chunks + question)
   and sends it to the local LLM via `llm/client.py` (Ollama's native `/api/chat`,
   not the OpenAI-compat `/v1` route — that endpoint silently ignores `keep_alive`).
4. Full response (not token-streamed to the client — see below) returned as JSON
   with source citations, refusal flag, and a per-query `query_log_id`.
5. The full exchange — question, retrieved chunks, citations the answer actually
   made, latency breakdown, refusal flag — is written to `query_logs`
   (`retrieval/store.py: log_query`). This backs both live monitoring
   (`/api/stats`, `/api/logs`) and offline eval — see
   [06-evaluation.md](06-evaluation.md).

Note: `chat_stream()` in `llm/client.py` streams tokens from Ollama, but the API layer
currently consumes the full generator before responding (`"".join(...)`) rather than
streaming to the frontend — the UI shows a typing indicator, not incremental tokens.
Revisit if perceived latency becomes a priority.

## Key interfaces (keep these stable as implementations change)

- `Embedder.embed(texts: list[str]) -> list[list[float]]`
- `VectorStore.upsert_document(...)`, `VectorStore.upsert_chunks(...)`,
  `VectorStore.search(query_vec, k) -> list[tuple[Chunk, Document]]`
- `LLMClient.chat_stream(user_message, context) -> Iterator[str]`

These interfaces are what let the LLM runtime or vector store change later without
touching ingestion or the API layer. They're also, as of the rtfm-hub project, a
de facto external library API — rtfm-hub imports and calls these directly rather than
going through `api/main.py`'s routes. `VectorStore.search()` and `LLMClient` both have
pending changes on the roadmap specifically because of that external consumer (a
document filter, and a pluggable provider interface, respectively) — check
`../rtfm-hub/docs/specs/01-architecture.md` before changing either signature.

## Database schema

`documents`: id, filename, title, content_hash, ingested_at
`chunks`: id, document_id (FK), page_number, chunk_index, content, embedding (vector),
  created_at
`query_logs`: id, question, answer, retrieved_chunks (jsonb), cited_sources (jsonb),
  refused, retrieval/embed/search/generation_latency_ms, feedback, created_at

pgvector index: HNSW on `chunks.embedding`, cosine distance. Full definitions in
`backend/src/ragapp/retrieval/schema.sql`.

Connections go through a `psycopg_pool.ConnectionPool` (not one connection per request —
that was a real perf bug, see git history) with pgvector types registered once per
pooled connection via the pool's `configure` hook.
