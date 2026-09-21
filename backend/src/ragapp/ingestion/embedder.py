import httpx

from ragapp.config import settings


class Embedder:
    """Wraps Ollama's /api/embeddings endpoint. Swap implementation to change
    embedding backend without touching ingestion/retrieval callers.

    Keeps one persistent httpx.Client per instance so repeated calls (e.g. one
    per chat request) reuse the underlying HTTP connection instead of paying
    connection setup cost every time.
    """

    def __init__(self, model: str | None = None, host: str | None = None):
        self.model = model or settings.embedding_model
        self.host = host or settings.ollama_host
        self._client = httpx.Client(base_url=self.host, timeout=60)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        response = self._client.post(
            "/api/embeddings",
            json={"model": self.model, "prompt": text, "keep_alive": settings.ollama_keep_alive},
        )
        response.raise_for_status()
        return response.json()["embedding"]
