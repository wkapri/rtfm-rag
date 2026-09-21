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
    """Ollama's OpenAI-compatible chat endpoint. Swap base_url/model to point at
    any other OpenAI-compatible local server without touching callers."""

    def __init__(self, model: str | None = None, host: str | None = None):
        self.model = model or settings.chat_model
        self.host = host or settings.ollama_host

    def chat_stream(self, user_message: str, context: str) -> Iterator[str]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_message}"},
        ]
        with httpx.Client(base_url=self.host, timeout=120) as client:
            with client.stream(
                "POST",
                "/v1/chat/completions",
                json={"model": self.model, "messages": messages, "stream": True},
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[len("data: ") :].strip()
                    if payload == "[DONE]":
                        break
                    delta = json.loads(payload)["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
