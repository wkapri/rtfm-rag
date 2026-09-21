from ragapp.ingestion.chunker import chunk_pages


def test_chunk_pages_preserves_page_numbers():
    pages = ["a" * 1000, "b" * 500]
    chunks = chunk_pages(pages, chunk_size=300, chunk_overlap=50)

    assert all(c.page_number in (1, 2) for c in chunks)
    assert chunks[0].page_number == 1
    assert chunks[-1].page_number == 2


def test_chunk_pages_skips_empty_pages():
    pages = ["content here", "   ", ""]
    chunks = chunk_pages(pages, chunk_size=100, chunk_overlap=10)

    assert len(chunks) == 1
    assert chunks[0].page_number == 1
