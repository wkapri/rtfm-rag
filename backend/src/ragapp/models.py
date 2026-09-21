from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    page_number: int
    chunk_index: int
    document_id: str | None = None
    embedding: list[float] | None = None


@dataclass
class Document:
    id: str
    filename: str
    title: str
