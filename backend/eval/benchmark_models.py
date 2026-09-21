"""Compare chat models on speed + answer quality against the ingested manual.

Retrieval is run once per question (model-independent) and reused across all
models, so this isolates generation performance specifically. Run from
backend/ with the venv active:

    python eval/benchmark_models.py
"""

import time

from ragapp.eval.heuristics import extract_citations, is_refusal
from ragapp.llm.client import LLMClient
from ragapp.retrieval.retriever import Retriever

MODELS = ["llama3.1", "llama3.2:3b", "qwen3:4b", "gemma3:4b"]

QUESTIONS = [
    "How do I restart the touchscreen?",
    "What tire pressure should I use?",
    "What is the top speed?",
    "How do I fold the mirrors?",
    "What is the meaning of life?",  # expect a refusal — not in the manual
]


def main() -> None:
    retriever = Retriever()

    # Retrieval is model-independent, so do it once and reuse for every model.
    retrieved_by_question = {q: retriever.retrieve(q) for q in QUESTIONS}

    for model in MODELS:
        print(f"\n{'=' * 70}\n{model}\n{'=' * 70}")
        client = LLMClient(model=model)

        latencies = []
        refusals = 0
        citation_hits = 0

        for question in QUESTIONS:
            results = retrieved_by_question[question]
            context = "\n\n".join(
                f"[{doc.filename}, page {chunk.page_number}]\n{chunk.content}" for chunk, doc in results
            )

            start = time.monotonic()
            try:
                answer = "".join(client.chat_stream(question, context))
            except Exception as exc:  # noqa: BLE001 — surface any model errors inline
                print(f"[{question}] ERROR: {exc}")
                continue
            latency_ms = int((time.monotonic() - start) * 1000)
            latencies.append(latency_ms)

            refused = is_refusal(answer)
            citations = extract_citations(answer, results)
            refusals += refused
            citation_hits += bool(citations)

            preview = answer.strip().replace("\n", " ")[:220]
            print(f"\n[{latency_ms}ms | refused={refused} | citations={len(citations)}] {question}")
            print(f"  -> {preview}...")

        if latencies:
            avg = sum(latencies) / len(latencies)
            print(f"\n{model} summary: avg={avg:.0f}ms  refusals={refusals}/{len(QUESTIONS)}  "
                  f"cited={citation_hits}/{len(QUESTIONS)}")


if __name__ == "__main__":
    main()
