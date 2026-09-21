# Overview

## Goal

Build a local RAG system that:

1. Ingests PDF instruction manuals (appliance manuals, device guides, etc.).
2. Chunks and embeds their content into a searchable vector store.
3. Lets a user ask questions in a chat UI, answered by a local LLM grounded in
   the relevant manual excerpts (with citations back to source document/page).

## Phase 1 (this machine, local-only)

- Single-user, single-machine setup.
- Manuals ingested manually via CLI (drop a PDF, run ingest command).
- Chat via a local web UI talking to a local FastAPI backend.
- Everything — DB, LLM, embeddings — runs on this Windows machine.

## Phase 2 (future, not building yet)

- Cloud deployment of the RAG backend independent of this machine, for demos.
- Home Assistant integration — e.g. "hey, how do I reset the error code on the
  dishwasher?" answered from ingested manuals via a HA conversation agent / intent.
- Possibly multi-user or shared knowledge base.

Phase 2 concerns should inform interface boundaries now (e.g. don't hardcode
localhost assumptions into core RAG logic) but shouldn't add complexity now.

## Non-goals (for now)

- Fine-tuning any model.
- Multi-tenant auth/permissions.
- OCR for scanned/image-only PDFs (revisit if a manual turns out to need it).
