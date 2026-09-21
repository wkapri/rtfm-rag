import httpx

from ragapp.config import settings


class Embedder:
    """Wraps Ollama's /api/embeddings endpoint. Swap implementation to change
    embedding backend without touching ingestion/retrieval callers."""

    def __init__(self, model: str | None = None, host: str | None = None):
        self.model = model or settings.embedding_model
        self.host = host or settings.ollama_host

    def embed(self, texts: list[str]) -> list[list[float]]:
        with httpx.Client(base_url=self.host, timeout=60) as client:
            return [self._embed_one(client, text) for text in texts]

    def _embed_one(self, client: httpx.Client, text: str) -> list[float]:
        response = client.post("/api/embeddings", json={"model": self.model, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]
