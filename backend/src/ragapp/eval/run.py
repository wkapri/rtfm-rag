from pathlib import Path

from ragapp.eval.dataset import EvalQuestion, load_dataset
from ragapp.eval.heuristics import extract_citations, is_refusal
from ragapp.eval.metrics import (
    PageRef,
    citation_accuracy,
    context_utilization,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from ragapp.llm.client import LLMClient
from ragapp.retrieval.retriever import Retriever


def run_eval(dataset_path: Path, top_k: int, with_generation: bool) -> None:
    questions = load_dataset(dataset_path)
    if not questions:
        print(f"No questions found in {dataset_path}")
        return

    retriever = Retriever()
    llm_client = LLMClient() if with_generation else None

    recalls, precisions, rrs = [], [], []
    citation_scores, utilizations, refusals = [], [], []

    for q in questions:
        relevant: set[PageRef] = {(q.document, page) for page in q.relevant_pages}
        results = retriever.retrieve(q.question, top_k=top_k)
        retrieved_pages: list[PageRef] = [(doc.filename, chunk.page_number) for chunk, doc in results]

        recall = recall_at_k(retrieved_pages, relevant)
        precision = precision_at_k(retrieved_pages, relevant)
        rr = reciprocal_rank(retrieved_pages, relevant)
        recalls.append(recall)
        precisions.append(precision)
        rrs.append(rr)

        line = f"[{recall:.2f} recall | {precision:.2f} prec | rr={rr:.2f}] {q.question}"

        if with_generation and llm_client is not None:
            context = "\n\n".join(
                f"[{doc.filename}, page {chunk.page_number}]\n{chunk.content}" for chunk, doc in results
            )
            answer = "".join(llm_client.chat_stream(q.question, context))
            refused = is_refusal(answer)
            cited = [(c["filename"], c["page"]) for c in extract_citations(answer, results)]

            refusals.append(refused)
            acc = citation_accuracy(cited, retrieved_pages)
            if acc is not None:
                citation_scores.append(acc)
            utilizations.append(context_utilization(cited, retrieved_pages))

            line += f" | refused={refused} | citation_acc={acc}"

        print(line)

    print()
    print(f"Questions:          {len(questions)}")
    print(f"Recall@{top_k}:          {_mean(recalls):.2f}")
    print(f"Precision@{top_k}:       {_mean(precisions):.2f}")
    print(f"MRR:                 {_mean(rrs):.2f}")
    if with_generation:
        print(f"Refusal rate:        {_mean([float(r) for r in refusals]):.2f}")
        print(f"Citation accuracy:   {_mean(citation_scores):.2f} (n={len(citation_scores)})")
        print(f"Context utilization: {_mean(utilizations):.2f}")


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
