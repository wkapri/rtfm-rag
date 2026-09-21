# rag1

Local RAG (Retrieval-Augmented Generation) system for PDF instruction manuals, with a
local LLM chatbot. See [CLAUDE.md](CLAUDE.md) for architecture/stack overview and
[docs/specs/](docs/specs/) for design docs.

## Prerequisites

None of these are installed yet on this machine. Install with `winget` (run in your own
PowerShell terminal, not something I run for you, since installers touch system state):

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
before `docker` commands work.

## First-time setup (once prerequisites are installed)

```powershell
# 1. Pull a local model
ollama pull llama3.1

# 2. Start Postgres + pgvector
docker compose up -d

# 3. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy ..\.env.example ..\.env
# edit .env if needed, then:
uvicorn ragapp.api.main:app --reload

# 4. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Ingesting a manual

```powershell
cd backend
python -m ragapp.cli ingest path\to\manual.pdf
```

## Project status

Early scaffolding. See [docs/specs/05-roadmap.md](docs/specs/05-roadmap.md).
