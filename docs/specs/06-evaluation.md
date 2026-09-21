# Evaluation & Monitoring

## Metrics (v1)

| Category | Metric | Source | Needs labels? |
|---|---|---|---|
| Retrieval | Recall@K | `eval` CLI vs. `eval/questions.yaml` | yes |
| Retrieval | Precision@K | `eval` CLI | yes |
| Retrieval | MRR | `eval` CLI | yes |
| Generation | Retrieval/generation latency split | live `query_logs` | no |
| Generation | Citation accuracy | `eval` CLI (`--with-generation`) or live logs | no (mechanical check) |
| Generation | Context utilization | same | no |
| Generation | Refusal rate | same | no (heuristic) |
| Generation | Faithfulness | not yet built | needs LLM-as-judge, treat as directional |
| Business | Thumbs up/down | live `query_logs.feedback` | no |
| Business | Query volume | live `query_logs` | no |

Dropped/deferred from the original brainstorm:
- **Resolution rate** — doesn't map to a manual-QA bot (no ticket concept);
  replaced by refusal rate / query success rate.
- **Cost per query** — $0 on local Ollama today; latency is the meaningful
  proxy until this runs on paid cloud infra (see roadmap Phase 3).

## Query logging

Every `/api/chat` call writes one row to `query_logs`
(`backend/src/ragapp/retrieval/schema.sql`): the question, answer, the
retrieved chunks (rank-ordered), the citations the model actually made,
a refusal flag, retrieval/generation latency, and (once submitted) thumbs
up/down feedback via `POST /api/feedback/{query_log_id}`.

This table is the single source for both live monitoring (latency trends,
refusal rate, feedback ratio over time) and part of offline eval (citation
accuracy, context utilization — these don't need ground-truth labels, just
the retrieved-vs-cited comparison).

## Offline eval (labeled)

Recall@K / Precision@K / MRR need ground truth: which pages actually answer
a given question. That lives in `backend/eval/questions.yaml`:

```yaml
- question: "How do I reset the touchscreen?"
  document: Tesla_Model_3_Owners_Manual.pdf
  relevant_pages: [7]
```

Run it:

```powershell
python -m ragapp.cli eval                    # retrieval metrics only (fast)
python -m ragapp.cli eval --with-generation   # + citation accuracy, refusal rate, context utilization (slow — one LLM call per question)
python -m ragapp.cli eval --top-k 3
```

Growing `questions.yaml` with real, representative questions (and getting
`relevant_pages` right) is the part that needs a human — the harness itself
is mechanical. See `backend/src/ragapp/eval/` for the implementation:

- `heuristics.py` — citation extraction and refusal detection (regex/keyword
  based, not an LLM judge — cheap and deterministic, but will miss phrasings
  it wasn't written for).
- `metrics.py` — pure scoring functions, one query at a time.
- `run.py` — CLI-facing runner that ties retrieval (+ optionally generation)
  to the labeled set and prints an aggregate report.

## Not built yet

- Faithfulness scoring (LLM-as-judge) — deferred until refusal
  rate/citation accuracy prove insufficient on their own.
- A dashboard over `query_logs` — for now, query it directly with SQL;
  revisit if this becomes a daily habit.
