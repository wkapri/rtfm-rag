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
   (`retrieval/retriever.py`) to get top-k relevant chunks.
3. Backend builds a prompt (system instructions + retrieved chunks + question)
   and sends it to the local LLM via `llm/client.py`.
4. Response streamed back to frontend, with source citations (filename + page)
   attached from the retrieved chunks.

## Key interfaces (keep these stable as implementations change)

- `Embedder.embed(texts: list[str]) -> list[list[float]]`
- `VectorStore.upsert(chunks: list[Chunk])`, `VectorStore.search(query_vec, k) -> list[Chunk]`
- `LLMClient.chat(messages: list[Message], stream: bool) -> ...`

These interfaces are what let the LLM runtime or vector store change later without
touching ingestion or the API layer.

## Database schema (initial)

`documents` table: id, filename, title, ingested_at
`chunks` table: id, document_id (FK), page_number, chunk_index, content, embedding (vector),
  created_at

pgvector index: HNSW or IVFFlat on `chunks.embedding`, cosine distance.
