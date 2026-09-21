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

- [ ] **Needed by rtfm-hub** (see `../rtfm-hub/docs/specs/05-roadmap.md` —
  consumed as a *library*, not an HTTP API, so these are function-signature changes,
  not new routes): add an optional `document_ids` filter to
  `VectorStore.search()`, and factor ingestion out of `cli.py` into a plain
  importable function (currently CLI-only, `raise SystemExit`s on bad input — needs
  to raise proper exceptions to be usable as a library call).
- [ ] **Needed by rtfm-hub**: pluggable LLM provider — `LLMClient` is currently
  Ollama-specific (native `/api/chat`, `keep_alive`, `num_ctx` options that don't
  generalize). Needs an interface with Ollama as the default implementation and
  OpenAI-compatible/Anthropic as swappable alternatives, so "bring your own LLM"
  is a config choice for both this app and rtfm-hub, not a rewrite.
- [ ] Ingest multiple manuals, verify retrieval quality across documents.
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
- [ ] Hybrid search / re-ranking if retrieval quality needs it.

Note: Home Assistant integration is being built as rtfm-hub (a separate repo that
imports this one as a library), not here — see `../rtfm-hub/docs/specs/`.
