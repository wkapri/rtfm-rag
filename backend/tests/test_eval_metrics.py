from ragapp.eval.metrics import (
    citation_accuracy,
    context_utilization,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)

DOC = "manual.pdf"


def test_recall_at_k_full_hit():
    retrieved = [(DOC, 1), (DOC, 5), (DOC, 9)]
    relevant = {(DOC, 5)}
    assert recall_at_k(retrieved, relevant) == 1.0


def test_recall_at_k_miss():
    retrieved = [(DOC, 1), (DOC, 2)]
    relevant = {(DOC, 5)}
    assert recall_at_k(retrieved, relevant) == 0.0


def test_precision_at_k():
    retrieved = [(DOC, 1), (DOC, 5), (DOC, 9), (DOC, 10)]
    relevant = {(DOC, 5), (DOC, 9)}
    assert precision_at_k(retrieved, relevant) == 0.5


def test_reciprocal_rank_first_hit():
    retrieved = [(DOC, 5), (DOC, 1)]
    relevant = {(DOC, 5)}
    assert reciprocal_rank(retrieved, relevant) == 1.0


def test_reciprocal_rank_second_hit():
    retrieved = [(DOC, 1), (DOC, 5)]
    relevant = {(DOC, 5)}
    assert reciprocal_rank(retrieved, relevant) == 0.5


def test_reciprocal_rank_no_hit():
    retrieved = [(DOC, 1), (DOC, 2)]
    relevant = {(DOC, 5)}
    assert reciprocal_rank(retrieved, relevant) == 0.0


def test_citation_accuracy_none_when_no_citations():
    assert citation_accuracy([], [(DOC, 1)]) is None


def test_citation_accuracy_detects_fabricated_citation():
    cited = [(DOC, 1), (DOC, 99)]
    retrieved = [(DOC, 1), (DOC, 2)]
    assert citation_accuracy(cited, retrieved) == 0.5


def test_context_utilization():
    cited = [(DOC, 1)]
    retrieved = [(DOC, 1), (DOC, 2), (DOC, 3)]
    assert context_utilization(cited, retrieved) == 1 / 3
