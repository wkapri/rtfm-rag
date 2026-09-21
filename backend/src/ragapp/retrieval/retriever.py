from ragapp.config import settings
from ragapp.ingestion.embedder import Embedder
from ragapp.models import Chunk, Document
from ragapp.retrieval.store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore | None = None, embedder: Embedder | None = None):
        self.store = store or VectorStore()
        self.embedder = embedder or Embedder()

    def retrieve(self, query: str, top_k: int | None = None) -> list[tuple[Chunk, Document]]:
        query_embedding = self.embedder.embed([query])[0]
        return self.store.search(query_embedding, top_k or settings.retrieval_top_k)
