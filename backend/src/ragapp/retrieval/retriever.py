import time
from dataclasses import dataclass

from ragapp.config import settings
from ragapp.ingestion.embedder import Embedder
from ragapp.models import Chunk, Document
from ragapp.retrieval.store import VectorStore


@dataclass
class RetrievalResult:
    results: list[tuple[Chunk, Document]]
    embed_latency_ms: int
    search_latency_ms: int


class Retriever:
    def __init__(self, store: VectorStore | None = None, embedder: Embedder | None = None):
        self.store = store or VectorStore()
        self.embedder = embedder or Embedder()

    def retrieve(self, query: str, top_k: int | None = None) -> list[tuple[Chunk, Document]]:
        return self.retrieve_with_timing(query, top_k).results

    def retrieve_with_timing(self, query: str, top_k: int | None = None) -> RetrievalResult:
        embed_start = time.monotonic()
        query_embedding = self.embedder.embed([query])[0]
        embed_latency_ms = int((time.monotonic() - embed_start) * 1000)

        search_start = time.monotonic()
        results = self.store.search(query_embedding, top_k or settings.retrieval_top_k)
        search_latency_ms = int((time.monotonic() - search_start) * 1000)

        return RetrievalResult(
            results=results, embed_latency_ms=embed_latency_ms, search_latency_ms=search_latency_ms
        )
