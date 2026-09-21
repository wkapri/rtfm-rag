import argparse
from pathlib import Path

from ragapp.config import settings
from ragapp.ingestion.chunker import chunk_pages
from ragapp.ingestion.embedder import Embedder
from ragapp.ingestion.pdf_loader import load_pdf_pages
from ragapp.retrieval.store import VectorStore, content_hash, init_schema


def ingest(path: Path, title: str | None) -> None:
    init_schema()
    pages = load_pdf_pages(path)
    full_text = "\n".join(pages)
    if not full_text.strip():
        raise SystemExit(f"No extractable text found in {path} (scanned PDF? needs OCR support).")

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
    print(f"Ingested {path.name}: {len(chunks)} chunks (document_id={document_id})")


def list_documents() -> None:
    store = VectorStore()
    for doc in store.list_documents():
        print(f"{doc.id}  {doc.filename}  ({doc.title})")


def main() -> None:
    parser = argparse.ArgumentParser(prog="ragapp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a PDF manual")
    ingest_parser.add_argument("path", type=Path)
    ingest_parser.add_argument("--title", default=None)

    subparsers.add_parser("list", help="List ingested documents")

    args = parser.parse_args()

    if args.command == "ingest":
        ingest(args.path, args.title)
    elif args.command == "list":
        list_documents()


if __name__ == "__main__":
    main()
