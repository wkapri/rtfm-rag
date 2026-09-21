from ragapp.eval.heuristics import extract_citations, is_refusal
from ragapp.models import Chunk, Document


def make_retrieved(filename: str, pages: list[int]) -> list[tuple[Chunk, Document]]:
    doc = Document(id="doc-1", filename=filename, title=filename)
    return [(Chunk(content="", page_number=p, chunk_index=i), doc) for i, p in enumerate(pages)]


def test_is_refusal_true_for_known_phrases():
    assert is_refusal("I don't know based on the provided manual excerpts.")
    assert is_refusal("The manual does not contain this information.")


def test_is_refusal_false_for_normal_answer():
    assert not is_refusal("Press and hold both scroll buttons to restart the touchscreen.")


def test_extract_citations_with_explicit_filename():
    retrieved = make_retrieved("manual.pdf", [7, 9])
    answer = "See manual.pdf, page 7 for details."
    citations = extract_citations(answer, retrieved)
    assert {"filename": "manual.pdf", "page": 7} in citations


def test_extract_citations_bare_page_single_document():
    retrieved = make_retrieved("manual.pdf", [7, 9])
    answer = "This is covered on page 9."
    citations = extract_citations(answer, retrieved)
    assert {"filename": "manual.pdf", "page": 9} in citations


def test_extract_citations_bare_page_ambiguous_with_multiple_documents():
    doc_a = Document(id="a", filename="a.pdf", title="a")
    doc_b = Document(id="b", filename="b.pdf", title="b")
    retrieved = [
        (Chunk(content="", page_number=7, chunk_index=0), doc_a),
        (Chunk(content="", page_number=9, chunk_index=0), doc_b),
    ]
    answer = "This is covered on page 9."
    citations = extract_citations(answer, retrieved)
    assert citations == []
