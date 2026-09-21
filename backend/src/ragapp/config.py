from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://ragapp:ragapp@localhost:5432/ragapp"

    # Which LLMProvider create_llm_client() builds: "ollama" (default, fully local),
    # "openai" (OpenAI or any OpenAI-compatible endpoint — set openai_base_url to
    # point elsewhere), or "anthropic". Embeddings stay Ollama-only regardless —
    # this only selects the chat/generation model.
    llm_provider: str = "ollama"

    # 127.0.0.1, not localhost: on Windows, "localhost" resolves to both ::1
    # and 127.0.0.1, and httpx's IPv6-then-fallback-to-IPv4 handshake costs
    # ~2s on every new connection — which is most connections, since httpx's
    # default keepalive expiry (5s) is shorter than a typical chat turn.
    ollama_host: str = "http://127.0.0.1:11434"
    chat_model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text"
    # How long Ollama keeps a model resident in VRAM after last use. Default
    # is 5m; both models here comfortably fit alongside each other in 4GB
    # VRAM, so there's no reason to pay reload cost on every idle gap.
    ollama_keep_alive: str = "30m"
    # llama3.2:3b's default 4096-token context doesn't leave enough VRAM
    # headroom (on a 4GB card, alongside nomic-embed-text) to fully offload
    # to GPU — it runs 80%/20% GPU/CPU split. 2048 is still comfortably
    # larger than our retrieval context (top_k=5 chunks is ~900 tokens) and
    # gets 100% GPU offload, ~16% more tokens/sec. Raise this if top_k or
    # chunk_size grow enough to risk truncating the prompt.
    ollama_chat_num_ctx: int = 2048

    # OpenAI-compatible provider (used when llm_provider="openai"). base_url lets
    # this point at any OpenAI-compatible endpoint, not just OpenAI itself.
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_chat_model: str = "gpt-4o-mini"

    # Anthropic provider (used when llm_provider="anthropic").
    anthropic_api_key: str | None = None
    anthropic_chat_model: str = "claude-haiku-4-5-20251001"

    chunk_size: int = 700
    chunk_overlap: int = 100
    retrieval_top_k: int = 5


settings = Settings()
