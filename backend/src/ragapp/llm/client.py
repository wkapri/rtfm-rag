import json
from collections.abc import Iterator

import httpx

from ragapp.config import settings

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using only the provided "
    "excerpts from instruction manuals. Cite the source filename and page number "
    "for claims you make. If the excerpts don't contain the answer, say so instead "
    "of guessing."
)


class LLMClient:
    """Ollama's native /api/chat endpoint (not the OpenAI-compat /v1 one — that
    endpoint silently ignores `keep_alive`, which defeats the point of setting
    it). If this ever needs to point at a different OpenAI-compatible server,
    swap this to /v1/chat/completions and drop keep_alive.

    Keeps one persistent httpx.Client per instance — see Embedder for why.
    """

    def __init__(self, model: str | None = None, host: str | None = None):
        self.model = model or settings.chat_model
        self.host = host or settings.ollama_host
        self._client = httpx.Client(base_url=self.host, timeout=120)

    def chat_stream(self, user_message: str, context: str) -> Iterator[str]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_message}"},
        ]
        with self._client.stream(
            "POST",
            "/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": True,
                "keep_alive": settings.ollama_keep_alive,
            },
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line.strip():
                    continue
                data = json.loads(line)
                delta = data.get("message", {}).get("content")
                if delta:
                    yield delta
                if data.get("done"):
                    break
