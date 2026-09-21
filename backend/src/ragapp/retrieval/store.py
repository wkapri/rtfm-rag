import hashlib
from contextlib import contextmanager
from pathlib import Path

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector

from ragapp.config import settings
from ragapp.models import Chunk, Document

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


@contextmanager
def get_connection():
    conn = psycopg.connect(settings.database_url, autocommit=True)
    try:
        register_vector(conn)
        yield conn
    finally:
        conn.close()


def init_schema() -> None:
    # Don't use get_connection() here: register_vector() requires the `vector`
    # type to already exist, but this is what creates it.
    conn = psycopg.connect(settings.database_url, autocommit=True)
    try:
        conn.execute(SCHEMA_PATH.read_text())
    finally:
        conn.close()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class VectorStore:
    def upsert_document(self, filename: str, title: str, full_text_hash: str) -> str:
        with get_connection() as conn:
            row = conn.execute(
                """
                INSERT INTO documents (filename, title, content_hash)
                VALUES (%s, %s, %s)
                ON CONFLICT (content_hash) DO UPDATE SET title = EXCLUDED.title
                RETURNING id
                """,
                (filename, title, full_text_hash),
            ).fetchone()
            return str(row[0])

    def upsert_chunks(self, document_id: str, chunks: list[Chunk]) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO chunks (document_id, page_number, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [
                        (document_id, c.page_number, c.chunk_index, c.content, Vector(c.embedding))
                        for c in chunks
                    ],
                )

    def search(self, query_embedding: list[float], top_k: int) -> list[tuple[Chunk, Document]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT c.content, c.page_number, c.chunk_index, d.id, d.filename, d.title
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                ORDER BY c.embedding <=> %s
                LIMIT %s
                """,
                (Vector(query_embedding), top_k),
            ).fetchall()
        return [
            (
                Chunk(content=r[0], page_number=r[1], chunk_index=r[2], document_id=str(r[3])),
                Document(id=str(r[3]), filename=r[4], title=r[5]),
            )
            for r in rows
        ]

    def list_documents(self) -> list[Document]:
        with get_connection() as conn:
            rows = conn.execute("SELECT id, filename, title FROM documents ORDER BY ingested_at").fetchall()
        return [Document(id=str(r[0]), filename=r[1], title=r[2]) for r in rows]
