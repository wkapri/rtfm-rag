# Roadmap

## Done

- [x] Repo scaffolding, specs, CLAUDE.md.

## Phase 1 — local MVP

- [ ] Install prerequisites (Python, Node, Docker, Ollama) — see [README.md](../../README.md).
- [ ] `docker compose up` — Postgres + pgvector running, schema created.
- [ ] Ingestion CLI: PDF → chunks → embeddings → DB, for one test manual.
- [ ] Retrieval: query → top-k chunks working from a Python REPL/script.
- [ ] FastAPI `/api/chat` endpoint wired to Ollama, grounded in retrieved chunks.
- [ ] Minimal React chat UI hitting the API, showing streamed answers + sources.

## Phase 2 — polish

- [ ] Ingest multiple manuals, verify retrieval quality across documents.
- [ ] Document-scoped queries ("only search manual X").
- [ ] Ingestion via UI upload instead of CLI-only.
- [ ] Basic auth if exposed beyond localhost.

## Phase 3 — future / exploratory

- [ ] Independent cloud deployment for demos.
- [ ] Home Assistant integration (conversation agent / custom intent).
- [ ] Hybrid search / re-ranking if retrieval quality needs it.
