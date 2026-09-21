"""Retrieval/generation metric primitives.

Each function scores a single query; callers average across queries to get
an aggregate (e.g. `mean(recall_at_k(...) for q in questions)`).
"""

PageRef = tuple[str, int]  # (filename, page_number)


def recall_at_k(retrieved: list[PageRef], relevant: set[PageRef]) -> float:
    """Fraction of the relevant pages that showed up anywhere in the retrieved set."""
    if not relevant:
        return 0.0
    hit = {page for page in retrieved if page in relevant}
    return len(hit) / len(relevant)


def precision_at_k(retrieved: list[PageRef], relevant: set[PageRef]) -> float:
    """Fraction of retrieved pages that were actually relevant."""
    if not retrieved:
        return 0.0
    hit = [page for page in retrieved if page in relevant]
    return len(hit) / len(retrieved)


def reciprocal_rank(retrieved: list[PageRef], relevant: set[PageRef]) -> float:
    """1/rank of the first relevant page in `retrieved` (1-indexed), else 0."""
    for rank, page in enumerate(retrieved, start=1):
        if page in relevant:
            return 1 / rank
    return 0.0


def citation_accuracy(cited: list[PageRef], retrieved: list[PageRef]) -> float | None:
    """Fraction of cited pages that were actually among the retrieved pages.

    Catches fabricated citations (the model naming a page it was never shown).
    Returns None when the answer made no citations to score — callers should
    exclude these from the aggregate rather than counting them as 0 or 1.
    """
    if not cited:
        return None
    retrieved_set = set(retrieved)
    hit = [page for page in cited if page in retrieved_set]
    return len(hit) / len(cited)


def context_utilization(cited: list[PageRef], retrieved: list[PageRef]) -> float:
    """Fraction of retrieved pages that made it into the answer's citations.

    Low values suggest top_k is fetching more than the model actually needs.
    """
    if not retrieved:
        return 0.0
    cited_set = set(cited)
    hit = [page for page in retrieved if page in cited_set]
    return len(hit) / len(set(retrieved))
