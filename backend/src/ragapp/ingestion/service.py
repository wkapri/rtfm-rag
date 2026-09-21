from pathlib import Path

from ragapp.config import settings
from ragapp.ingestion.chunker import chunk_pages
from ragapp.ingestion.embedder import Embedder
from ragapp.ingestion.pdf_loader import load_pdf_pages
from ragapp.retrieval.store import VectorStore, content_hash, init_schema


class IngestionError(Exception):
    """A PDF couldn't be ingested (e.g. no extractable text)."""


def ingest_pdf(path: Path, title: str | None = None) -> tuple[str, int]:
    """Ingest a PDF manual: load, chunk, embed, store. Returns (document_id, chunk_count).

    Callable directly as a library function (e.g. by rtfm-hub's discovery agent after
    downloading a manual) — raises IngestionError on failure rather than exiting the
    process, unlike the CLI wrapper in cli.py. Ensures the schema exists first, so
    it's safe to call as the very first database operation in a fresh app.
    """
    init_schema()
    pages = load_pdf_pages(path)
    full_text = "\n".join(pages)
    if not full_text.strip():
        raise IngestionError(
            f"No extractable text found in {path} (scanned PDF? needs OCR support)."
        )

    store = VectorStore()
    document_id = store.upsert_document(
        filename=path.name,
        title=title or path.stem,
        full_text_hash=content_hash(full_text),
    )

    chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
    embedder = Embedder()
    embeddings = embedder.embed([c.content for c in chunks])
    for chunk, embedding in zip(chunks, embeddings, strict=True):
        chunk.embedding = embedding
        chunk.document_id = document_id

    store.upsert_chunks(document_id, chunks)
    return document_id, len(chunks)
