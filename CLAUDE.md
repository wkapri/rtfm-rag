# rag1 — Local RAG for PDF Instruction Manuals

## What this is

A local-first RAG (Retrieval-Augmented Generation) system:
- Ingests PDF instruction manuals into a searchable knowledge base.
- Serves answers through a local LLM chatbot, grounded in the ingested manuals.
- Runs entirely on-device for now. Designed so pieces (LLM, vector store) can later
  move to the cloud independently, or integrate with Home Assistant.

## Stack

| Layer          | Choice                                  | Notes |
|----------------|------------------------------------------|-------|
| Backend/RAG    | Python                                    | ingestion, embedding, retrieval, API |
| Frontend       | React + TypeScript (Vite)                 | chat UI |
| Vector store   | PostgreSQL + pgvector                     | run locally via Docker |
| LLM runtime    | Ollama (default, swappable)               | OpenAI-compatible local API |
| API            | FastAPI (Python)                          | serves frontend + does retrieval/generation orchestration |

Node.js is only required for the frontend (npm, Vite dev server) — the RAG core is pure Python.

## Repo layout

```
rag1/
  backend/           Python RAG core + API (see backend/README.md)
    src/ragapp/
      ingestion/      PDF loading, chunking, embedding
      retrieval/      pgvector store + retriever
      llm/            LLM client (Ollama by default)
      api/            FastAPI app
  frontend/          React + TS chat UI (Vite)
  docs/specs/        Design docs — read these before making architectural changes
  docker-compose.yml  Postgres + pgvector service
  data/manuals/      Source PDFs (gitignored — local only)
```

## Conventions

- Keep ingestion, retrieval, and LLM-client code as separate modules with clear
  interfaces — the LLM runtime and vector store are both expected to change later
  (e.g. cloud deployment, Home Assistant integration), so avoid tight coupling.
- Config (DB URL, Ollama host/model, embedding model) lives in env vars — see
  `.env.example`. Never hardcode secrets or local paths.
- Prefer small, testable functions in `ingestion/` and `retrieval/` over notebook-style
  scripts — this will need to run unattended later (e.g. drop a PDF in a folder → auto-ingest).

## Current status

Early scaffolding stage. See [docs/specs/05-roadmap.md](docs/specs/05-roadmap.md) for what's
built vs. planned.

## Prerequisites (not yet installed on this machine)

- Python 3.11+
- Node.js 20+ (frontend only)
- Docker Desktop (for Postgres + pgvector; Ollama can run natively on Windows instead of Docker)
- Ollama (https://ollama.com) — for the local LLM

See [README.md](README.md) for install commands.
