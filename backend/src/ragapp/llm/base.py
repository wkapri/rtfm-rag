from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using only the provided "
    "excerpts from instruction manuals. Cite the source filename and page number "
    "for claims you make. If the excerpts don't contain the answer, say so instead "
    "of guessing."
)


def build_user_content(user_message: str, context: str) -> str:
    return f"Context:\n{context}\n\nQuestion: {user_message}"


@dataclass
class ToolSpec:
    """A tool definition offered to the model in complete_with_tools() — name,
    description, and its arguments' JSON schema. Providers translate this into
    their own wire format (Anthropic's input_schema, OpenAI's parameters, etc.)."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class AssistantTurn:
    """One turn from the model in a tool-calling loop: zero or more tool calls
    it wants executed, and/or plain text. A caller running an agent loop (see
    rtfm-hub's hubapp.agent) generally treats a turn with no tool_calls as the
    model having stopped without reaching a designated terminal tool — that's
    usually a loop error, not a valid way to finish, since terminal answers are
    meant to arrive as a structured tool call, not free text.
    """

    tool_calls: list[ToolCall] = field(default_factory=list)
    text: str | None = None


# The message format complete_with_tools() takes, independent of any one
# provider's wire format:
#   {"role": "user", "content": "..."}
#   {"role": "assistant", "content": str | None, "tool_calls": list[ToolCall]}
#   {"role": "tool", "tool_call_id": "...", "content": "..."}
Message = dict[str, Any]


class LLMProvider(Protocol):
    """Common interface every chat backend implements — Ollama, OpenAI-compatible,
    Anthropic, whatever comes next. Callers (the API layer, eval harness, rtfm-hub)
    depend only on this, never on a specific provider's constructor or request shape.

    system_prompt defaults to this module's SYSTEM_PROMPT (the RAG manual-Q&A
    instructions) so existing callers are unaffected, but can be overridden —
    rtfm-hub uses this for non-RAG tasks like product identification, which have
    nothing to do with answering from manual excerpts.
    """

    def chat_stream(
        self, user_message: str, context: str, system_prompt: str | None = None
    ) -> Iterator[str]: ...

    def complete_with_tools(
        self, messages: list[Message], tools: list[ToolSpec], system_prompt: str
    ) -> AssistantTurn:
        """Non-streaming: send the running conversation plus available tool
        definitions, get back either tool call(s) to execute or final text.
        For agentic tool-use loops (rtfm-hub's product-identification and
        manual-discovery agents) — never used for RAG chat, which stays on
        chat_stream (streaming, no tool concept)."""
        ...
