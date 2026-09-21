import json
from collections.abc import Iterator

import httpx

from ragapp.llm.base import SYSTEM_PROMPT, build_user_content

ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider:
    """Anthropic's Messages API (api.anthropic.com/v1/messages) — different auth
    header, different request/response shape from the OpenAI-style providers, so
    this isn't a thin variant of OpenAICompatProvider.

    Keeps one persistent httpx.Client per instance — see Embedder for why.
    """

    def __init__(self, api_key: str, model: str, max_tokens: int = 1024):
        self.model = model
        self.max_tokens = max_tokens
        self._client = httpx.Client(
            base_url="https://api.anthropic.com/v1",
            headers={
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_VERSION,
            },
            timeout=120,
        )

    def chat_stream(self, user_message: str, context: str) -> Iterator[str]:
        with self._client.stream(
            "POST",
            "/messages",
            json={
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": build_user_content(user_message, context)}],
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line.startswith("data: "):
                    continue
                data = json.loads(line[len("data: ") :])
                if data.get("type") == "content_block_delta":
                    delta = data.get("delta", {}).get("text")
                    if delta:
                        yield delta
