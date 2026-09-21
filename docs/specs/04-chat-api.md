# Chat API

## Endpoints (initial)

- `POST /api/chat` — body: `{ message: string, document_id?: string }`.
  Returns streamed response (SSE or chunked) with final message + `sources: [{filename, page}]`.
- `GET /api/documents` — list ingested documents (id, filename, title, ingested_at).
- `POST /api/documents` — upload + trigger ingestion of a new PDF (later; CLI-only for now).
- `GET /api/health` — basic health check (DB reachable, Ollama reachable).

## LLM client

Default: Ollama's OpenAI-compatible endpoint (`http://localhost:11434/v1`), so
swapping to a different OpenAI-compatible local server (llama.cpp server, LM Studio)
later is a config change, not a code change.

## Frontend

Simple chat UI: message list, input box, streaming response rendering, and a
collapsible "sources" section per answer showing which manual/page was used.
