# Roadmap

## Done

- [x] Repo scaffolding, specs, CLAUDE.md.

## Phase 1 — local MVP

- [x] Install prerequisites (Python, Node, Docker, Ollama) — see [README.md](../../README.md).
- [x] `docker compose up` — Postgres + pgvector running, schema created.
- [x] Ingestion CLI: PDF → chunks → embeddings → DB (Tesla Model 3 manual, 1498 chunks).
- [x] Retrieval: query → top-k chunks, verified against real questions.
- [x] FastAPI `/api/chat` endpoint wired to Ollama, grounded in retrieved chunks.
- [x] Minimal React chat UI hitting the API, showing answers + sources.
- [x] Eval/monitoring: `query_logs` table, Recall@K/MRR/citation-accuracy harness
  (`python -m ragapp.cli eval`), Stats panel + per-answer Details panel in the UI —
  see [06-evaluation.md](06-evaluation.md).
- [x] Performance pass: connection pooling, persistent HTTP clients, model swap
  (llama3.1 → llama3.2:3b), `keep_alive`, IPv4 host fix, full GPU offload via
  `num_ctx`. Retrieval 3-4s → ~200ms, generation 17-30s → 5-8s.

## Phase 2 — polish

- [ ] Ingest multiple manuals, verify retrieval quality across documents.
- [ ] Document-scoped queries ("only search manual X").
- [ ] Ingestion via UI upload instead of CLI-only.
- [ ] Basic auth if exposed beyond localhost.
- [ ] Fill out `backend/eval/questions.yaml` with a real labeled question set
  (currently just a template) and run Recall@K/MRR for real.
- [ ] Fix refusal-detection heuristic gaps found during model benchmarking
  (`heuristics.py` misses phrasings like "do not contain" / "not aware of any
  information" — only catches "does not contain").
- [ ] Benchmark `llama3.2:1b` — smaller/faster than the current `llama3.2:3b`
  default; worth trying if answer latency matters more than depth for some
  use cases. Trade-off is untested quality loss at this size.

## Phase 3 — future / exploratory

- [ ] Independent cloud deployment for demos.
- [ ] Home Assistant integration (conversation agent / custom intent).
- [ ] Hybrid search / re-ranking if retrieval quality needs it.
