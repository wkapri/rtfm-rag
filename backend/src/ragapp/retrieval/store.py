import hashlib
from contextlib import contextmanager
from pathlib import Path

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from ragapp.config import settings
from ragapp.models import Chunk, Document

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

# Lazily created: must come after init_schema() has run, since the pool's
# `configure` hook (register_vector) requires the `vector` type to already
# exist. Pooling connections (rather than opening one per call, as before)
# avoids paying TCP + pgvector type registration cost on every single query.
_pool: ConnectionPool | None = None


def _configure_connection(conn: psycopg.Connection) -> None:
    register_vector(conn)


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            settings.database_url,
            min_size=1,
            max_size=5,
            configure=_configure_connection,
            kwargs={"autocommit": True},
        )
    return _pool


@contextmanager
def get_connection():
    with _get_pool().connection() as conn:
        yield conn


def init_schema() -> None:
    # Don't use get_connection()/the pool here: register_vector() requires
    # the `vector` type to already exist, but this is what creates it.
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

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[tuple[Chunk, Document]]:
        # document_ids is None -> search every ingested document (unchanged default
        # behavior). Pass a list to scope the search, e.g. to one product's manual.
        filter_sql = "AND c.document_id = ANY(%(document_ids)s::uuid[])" if document_ids else ""
        with get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT c.id, c.content, c.page_number, c.chunk_index, d.id, d.filename, d.title
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE true
                {filter_sql}
                ORDER BY c.embedding <=> %(query_embedding)s
                LIMIT %(top_k)s
                """,
                {
                    "document_ids": document_ids,
                    "query_embedding": Vector(query_embedding),
                    "top_k": top_k,
                },
            ).fetchall()
        return [
            (
                Chunk(id=str(r[0]), content=r[1], page_number=r[2], chunk_index=r[3], document_id=str(r[4])),
                Document(id=str(r[4]), filename=r[5], title=r[6]),
            )
            for r in rows
        ]

    def list_documents(self) -> list[Document]:
        with get_connection() as conn:
            rows = conn.execute("SELECT id, filename, title FROM documents ORDER BY ingested_at").fetchall()
        return [Document(id=str(r[0]), filename=r[1], title=r[2]) for r in rows]

    def log_query(
        self,
        question: str,
        answer: str,
        retrieved_chunks: list[dict],
        cited_sources: list[dict],
        refused: bool,
        retrieval_latency_ms: int,
        generation_latency_ms: int,
        embed_latency_ms: int | None = None,
        search_latency_ms: int | None = None,
    ) -> str:
        with get_connection() as conn:
            row = conn.execute(
                """
                INSERT INTO query_logs
                    (question, answer, retrieved_chunks, cited_sources, refused,
                     retrieval_latency_ms, embed_latency_ms, search_latency_ms, generation_latency_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    question,
                    answer,
                    Jsonb(retrieved_chunks),
                    Jsonb(cited_sources),
                    refused,
                    retrieval_latency_ms,
                    embed_latency_ms,
                    search_latency_ms,
                    generation_latency_ms,
                ),
            ).fetchone()
            return str(row[0])

    def set_feedback(self, query_log_id: str, feedback: int) -> None:
        with get_connection() as conn:
            conn.execute(
                "UPDATE query_logs SET feedback = %s WHERE id = %s", (feedback, query_log_id)
            )

    def list_query_logs(self, limit: int = 20) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, question, answer, retrieved_chunks, cited_sources, refused,
                       retrieval_latency_ms, embed_latency_ms, search_latency_ms,
                       generation_latency_ms, feedback, created_at
                FROM query_logs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()
        columns = [
            "id", "question", "answer", "retrieved_chunks", "cited_sources", "refused",
            "retrieval_latency_ms", "embed_latency_ms", "search_latency_ms",
            "generation_latency_ms", "feedback", "created_at",
        ]
        return [dict(zip(columns, row, strict=True)) for row in rows]

    def get_stats(self) -> dict:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    count(*) AS total_queries,
                    avg(retrieval_latency_ms) AS avg_retrieval_latency_ms,
                    avg(generation_latency_ms) AS avg_generation_latency_ms,
                    avg(case when refused then 1.0 else 0.0 end) AS refusal_rate,
                    count(*) FILTER (WHERE feedback = 1) AS thumbs_up,
                    count(*) FILTER (WHERE feedback = -1) AS thumbs_down,
                    count(*) FILTER (WHERE feedback IS NOT NULL) AS feedback_count
                FROM query_logs
                """
            ).fetchone()
        return {
            "total_queries": row[0],
            "avg_retrieval_latency_ms": round(row[1]) if row[1] is not None else None,
            "avg_generation_latency_ms": round(row[2]) if row[2] is not None else None,
            "refusal_rate": round(row[3], 3) if row[3] is not None else None,
            "thumbs_up": row[4],
            "thumbs_down": row[5],
            "feedback_count": row[6],
        }
