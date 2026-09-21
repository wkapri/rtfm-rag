import json
from collections.abc import Iterator

import httpx

from ragapp.config import settings
from ragapp.llm.base import SYSTEM_PROMPT, build_user_content


class OllamaProvider:
    """Ollama's native /api/chat endpoint (not the OpenAI-compat /v1 one — that
    endpoint silently ignores `keep_alive`, which defeats the point of setting
    it).

    Keeps one persistent httpx.Client per instance — see Embedder for why.
    """

    def __init__(self, model: str | None = None, host: str | None = None):
        self.model = model or settings.chat_model
        self.host = host or settings.ollama_host
        self._client = httpx.Client(base_url=self.host, timeout=120)

    def chat_stream(self, user_message: str, context: str) -> Iterator[str]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_content(user_message, context)},
        ]
        with self._client.stream(
            "POST",
            "/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": True,
                "keep_alive": settings.ollama_keep_alive,
                "options": {"num_ctx": settings.ollama_chat_num_ctx},
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
