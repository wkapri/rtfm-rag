# Chat API

## Endpoints (as built)

- `POST /api/chat` — body: `{ message: string }`. Returns JSON (not streamed — see
  [01-architecture.md](01-architecture.md) for why):
  `{ answer, sources: [{filename, page}], query_log_id, refused, retrieval_latency_ms,
  embed_latency_ms, search_latency_ms, generation_latency_ms, retrieved_chunks: [{rank,
  filename, page, preview}] }`.
- `POST /api/feedback/{query_log_id}` — body: `{ feedback: 1 | -1 }`. Thumbs up/down on
  a previous answer.
- `GET /api/documents` — list ingested documents (id, filename, title).
- `GET /api/stats` — aggregate metrics: total queries, avg retrieval/generation latency,
  refusal rate, thumbs up/down counts.
- `GET /api/logs?limit=N` — recent `query_logs` rows for the Stats panel.
- `GET /api/health` — basic liveness check.

Not built: document-scoped queries (`document_id` filter), PDF upload via the API
(CLI-only for now — see [02-ingestion.md](02-ingestion.md)).

## LLM client

Ollama's **native** `/api/chat` endpoint, not the OpenAI-compat `/v1/chat/completions`
route — the compat endpoint silently ignores the `keep_alive` parameter, which defeats
the point of setting it (see `llm/client.py` docstring). This means swapping to a
different backend later is a slightly bigger change than "just repoint the base URL" —
budget for adapting the request/response shape if that ever happens.

## Frontend

React chat UI (`frontend/src/`): message bubbles with source citations, a collapsible
per-answer "how this answer was built" panel (retrieval/generation latency breakdown +
retrieved chunks), thumbs up/down feedback, and a slide-over Stats drawer. Dark mode
follows system preference via CSS custom properties (`styles.css`) — no toggle needed.
