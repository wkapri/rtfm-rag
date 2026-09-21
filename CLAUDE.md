# rtfm-rag — Local RAG for PDF Instruction Manuals

## What this is

A local-first RAG (Retrieval-Augmented Generation) system:
- Ingests PDF instruction manuals into a searchable knowledge base.
- Serves answers through a local LLM chatbot, grounded in the ingested manuals.
- Logs every query (retrieval + generation latency, citations, feedback) for monitoring
  and offline eval — see [docs/specs/06-evaluation.md](docs/specs/06-evaluation.md).
- Runs entirely on-device for now. Designed so pieces (LLM, vector store) can later
  move to the cloud independently.

**Also designed to be used as a library, not just a standalone app.**
[rtfm-hub](../rtfm-hub) (a sibling project — personal inventory + manual-discovery
agent, eventually a Home Assistant add-on) imports `ragapp` directly and shares this
app's Postgres database rather than calling it over HTTP. Keep that in mind when
changing `ingestion/`, `retrieval/`, or `llm/`: those modules have a consumer outside
this repo, even though nothing here imports rtfm-hub back. Two things already built
because of that: `VectorStore.search()` takes an optional `document_ids` filter, and
the chat LLM is a pluggable `LLMProvider` (`llm/factory.py`'s `create_llm_client()`)
rather than an Ollama-specific class — see the Stack table below.

## Stack

| Layer          | Choice                                  | Notes |
|----------------|------------------------------------------|-------|
| Backend/RAG    | Python                                    | ingestion, embedding, retrieval, API |
| Frontend       | React + TypeScript (Vite)                 | chat UI |
| Vector store   | PostgreSQL + pgvector                     | run locally via Docker |
| LLM runtime    | Pluggable via `LLM_PROVIDER` env var: `ollama` (default, native `/api/chat` — not the OpenAI-compat `/v1` route, which silently ignores `keep_alive`), `openai` (OpenAI or any OpenAI-compatible endpoint), or `anthropic` | default provider `ollama`, model `llama3.2:3b`, all swappable via `.env` |
| API            | FastAPI (Python)                          | serves frontend + does retrieval/generation orchestration |

Node.js is only required for the frontend (npm, Vite dev server) — the RAG core is pure Python.

## Repo layout

```
rtfm-rag/
  backend/
    src/ragapp/
      ingestion/      PDF loading, chunking, embedding, service.py (importable ingest_pdf())
      retrieval/      pgvector store + retriever
      llm/            base.py (LLMProvider interface), factory.py, providers/ (ollama, openai_compat, anthropic)
      eval/           Citation/refusal heuristics, Recall@K/MRR/etc., CLI eval runner
      api/            FastAPI app (chat, feedback, stats/logs, documents)
    eval/             questions.yaml (labeled eval set) + benchmark_models.py
    tests/
  frontend/
    src/             React + TS chat UI (Vite) — components, styles.css (design tokens, dark mode)
  docs/specs/        Design docs — read these before making architectural changes
  docker-compose.yml  Postgres + pgvector service
  data/manuals/      Source PDFs (gitignored — local only)
```

## Conventions

- Keep ingestion, retrieval, and LLM-client code as separate modules with clear
  interfaces — the LLM runtime and vector store are both expected to change later,
  and rtfm-hub imports these modules directly as a library, so avoid tight coupling
  and avoid anything that only makes sense in the context of this app's own FastAPI
  routes.
- Config (DB URL, Ollama host/model, embedding model) lives in env vars — see
  `.env.example`. Never hardcode secrets or local paths.
- Prefer small, testable functions in `ingestion/` and `retrieval/` over notebook-style
  scripts — this will need to run unattended later (e.g. drop a PDF in a folder → auto-ingest).

## Current status

Phase 1 (local MVP) is done — ingestion, retrieval, chat, eval harness, monitoring, and a
performance-tuned local model all work end to end. See
[docs/specs/05-roadmap.md](docs/specs/05-roadmap.md) for what's built vs. planned.

## Prerequisites

- Python 3.11+
- Node.js 20+ (frontend only)
- Docker Desktop (for Postgres + pgvector; Ollama can run natively on Windows instead of Docker)
- Ollama (https://ollama.com) — for the local LLM

See [README.md](README.md) for install + setup commands.
