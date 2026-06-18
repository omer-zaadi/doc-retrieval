import logging
import os
from typing import Any

import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection as PgConnection

logger = logging.getLogger(__name__)


def get_connection() -> PgConnection:
    url = os.environ["POSTGRES_URL"]
    try:
        conn = psycopg2.connect(url)
        logger.debug("Connected to database.")
        return conn
    except psycopg2.OperationalError as exc:
        raise psycopg2.OperationalError(
            f"Could not connect to database. Is the server running?\nDetails: {exc}"
        ) from exc


def init_schema(conn: PgConnection) -> None:
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id              SERIAL PRIMARY KEY,
                chunk_text      TEXT            NOT NULL,
                embedding       vector(768),
                filename        TEXT            NOT NULL,
                split_strategy  VARCHAR(50)     NOT NULL,
                created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_embedding
            ON document_chunks
            USING hnsw (embedding vector_cosine_ops);
        """)
    conn.commit()
    logger.debug("Schema ready.")


def insert_chunks(
    conn: PgConnection,
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str,
    split_strategy: str,
) -> int:
    """Insert text chunks with their embeddings. Returns number of inserted rows."""
    rows = list(zip(chunks, embeddings))
    with conn.cursor() as cur:
        for chunk, embedding in rows:
            cur.execute(
                """
                INSERT INTO document_chunks (chunk_text, embedding, filename, split_strategy)
                VALUES (%s, %s::vector, %s, %s)
                """,
                (chunk, str(embedding), filename, split_strategy),
            )
    conn.commit()
    logger.debug("Inserted %d rows for '%s'.", len(rows), filename)
    return len(rows)


def search_similar(
    conn: PgConnection,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[tuple[Any, ...]]:
    """Return top-k chunks by cosine similarity to the query embedding."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                chunk_text,
                filename,
                split_strategy,
                created_at,
                (embedding <=> %s::vector) AS cosine_distance
            FROM document_chunks
            ORDER BY cosine_distance ASC
            LIMIT %s;
            """,
            (str(query_embedding), top_k),
        )
        return cur.fetchall()
