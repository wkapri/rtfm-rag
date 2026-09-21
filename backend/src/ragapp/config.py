from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://ragapp:ragapp@localhost:5432/ragapp"

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

    chunk_size: int = 700
    chunk_overlap: int = 100
    retrieval_top_k: int = 5


settings = Settings()
