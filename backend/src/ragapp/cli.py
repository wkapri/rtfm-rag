import argparse
from pathlib import Path

from ragapp.config import settings
from ragapp.eval.run import run_eval
from ragapp.ingestion.service import IngestionError, ingest_pdf
from ragapp.retrieval.store import VectorStore


def ingest(path: Path, title: str | None) -> None:
    try:
        document_id, chunk_count = ingest_pdf(path, title)
    except IngestionError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Ingested {path.name}: {chunk_count} chunks (document_id={document_id})")


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

    eval_parser = subparsers.add_parser("eval", help="Run retrieval/generation eval against a labeled question set")
    eval_parser.add_argument("dataset", type=Path, nargs="?", default=Path(__file__).parent.parent.parent / "eval" / "questions.yaml")
    eval_parser.add_argument("--top-k", type=int, default=settings.retrieval_top_k)
    eval_parser.add_argument(
        "--with-generation",
        action="store_true",
        help="Also run each question through the LLM to score refusal rate, citation accuracy, and context utilization (slow).",
    )

    args = parser.parse_args()

    if args.command == "ingest":
        ingest(args.path, args.title)
    elif args.command == "list":
        list_documents()
    elif args.command == "eval":
        run_eval(args.dataset, args.top_k, args.with_generation)


if __name__ == "__main__":
    main()
