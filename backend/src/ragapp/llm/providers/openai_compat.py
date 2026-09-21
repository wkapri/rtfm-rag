import json
from collections.abc import Iterator

import httpx

from ragapp.llm.base import SYSTEM_PROMPT, build_user_content


class OpenAICompatProvider:
    """Works against OpenAI itself, or any endpoint that mirrors OpenAI's
    /chat/completions API — many cloud and self-hosted providers do (vLLM,
    LM Studio, OpenRouter, etc.). Point base_url elsewhere to use those.

    Keeps one persistent httpx.Client per instance — see Embedder for why.
    """

    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1"):
        self.model = model
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=120,
        )

    def chat_stream(
        self, user_message: str, context: str, system_prompt: str | None = None
    ) -> Iterator[str]:
        messages = [
            {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
            {"role": "user", "content": build_user_content(user_message, context)},
        ]
        with self._client.stream(
            "POST",
            "/chat/completions",
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
