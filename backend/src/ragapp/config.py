from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://ragapp:ragapp@localhost:5432/ragapp"

    ollama_host: str = "http://localhost:11434"
    chat_model: str = "llama3.1"
    embedding_model: str = "nomic-embed-text"

    chunk_size: int = 700
    chunk_overlap: int = 100
    retrieval_top_k: int = 5


settings = Settings()
