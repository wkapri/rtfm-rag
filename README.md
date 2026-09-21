# rag1

Local RAG (Retrieval-Augmented Generation) system for PDF instruction manuals, with a
local LLM chatbot. See [CLAUDE.md](CLAUDE.md) for architecture/stack overview and
[docs/specs/](docs/specs/) for design docs. [MIT licensed](LICENSE).

## Prerequisites

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Docker.DockerDesktop
winget install -e --id Ollama.Ollama
```

After installing, **restart your terminal** so PATH updates take effect, then verify:

```powershell
python --version
node --version
npm --version
docker --version
ollama --version
```

Docker Desktop needs to be launched once manually and given a minute to start its engine
before `docker` commands work. If it fails with a virtualization error, VT-x/AMD-V needs
enabling in your BIOS/UEFI (reboot → firmware settings → enable virtualization).

## First-time setup

```powershell
# 1. Pull the local models (chat + embedding — both required)
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# 2. Start Postgres + pgvector
docker compose up -d

# 3. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy ..\.env.example ..\.env
uvicorn ragapp.api.main:app --reload

# 4. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

`llama3.2:3b` is the default chat model — chosen after benchmarking it against
llama3.1, qwen3:4b, and gemma3:4b (see `backend/eval/benchmark_models.py`) as the best
speed/quality tradeoff on a 4GB-VRAM GPU. If you have more VRAM to spare, a larger
model (e.g. `llama3.1`) may give better answers at the cost of latency — change
`CHAT_MODEL` in `.env` and restart the backend.

## Ingesting a manual

```powershell
cd backend
python -m ragapp.cli ingest path\to\manual.pdf
python -m ragapp.cli list          # see what's ingested
```

## Evaluating retrieval/generation quality

```powershell
cd backend
python -m ragapp.cli eval                    # Recall@K / Precision@K / MRR (fast, no LLM calls)
python -m ragapp.cli eval --with-generation   # + refusal rate, citation accuracy, context utilization (slower)
```

Scored against `backend/eval/questions.yaml` — a labeled question set you fill in
yourself (see the template comment in that file). See
[docs/specs/06-evaluation.md](docs/specs/06-evaluation.md) for what each metric means.

## Monitoring

Every chat request is logged (question, retrieved chunks, latency breakdown, thumbs
up/down feedback) to the `query_logs` table. View it via:

- The **Stats** button in the chat UI (top right) — aggregate metrics + recent queries.
- The **"how this answer was built"** disclosure under each answer — per-query retrieval
  timing and which chunks were used.
- `GET /api/stats` / `GET /api/logs` directly.
- SQL, for anything deeper: `docker exec rag1-db-1 psql -U ragapp -d ragapp`

## Using it from your phone (same network)

The dev servers bind to your LAN interface by default. Find your machine's IP
(`ipconfig`, look for the Ethernet/Wi-Fi adapter's IPv4 address) and open
`http://<that-ip>:5173` on your phone, same Wi-Fi network. You may need to allow ports
5173 and 8000 through Windows Firewall (Windows Defender Firewall → Advanced settings →
Inbound Rules → New Rule).

## Project status

Phase 1 (local MVP) is done: ingestion, retrieval, chat, eval harness, monitoring, and
a tuned local model are all working end to end. See
[docs/specs/05-roadmap.md](docs/specs/05-roadmap.md) for what's next.
