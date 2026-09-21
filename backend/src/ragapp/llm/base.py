from collections.abc import Iterator
from typing import Protocol

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using only the provided "
    "excerpts from instruction manuals. Cite the source filename and page number "
    "for claims you make. If the excerpts don't contain the answer, say so instead "
    "of guessing."
)


def build_user_content(user_message: str, context: str) -> str:
    return f"Context:\n{context}\n\nQuestion: {user_message}"


class LLMProvider(Protocol):
    """Common interface every chat backend implements — Ollama, OpenAI-compatible,
    Anthropic, whatever comes next. Callers (the API layer, eval harness, rtfm-hub)
    depend only on this, never on a specific provider's constructor or request shape.
    """

    def chat_stream(self, user_message: str, context: str) -> Iterator[str]: ...
