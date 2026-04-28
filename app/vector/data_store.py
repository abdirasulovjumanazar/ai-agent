import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector

from app.db.connection import get_engine
from app.vector.embedder import embed
from app.vector.chunker import build_all_chunks
from app.config import settings
from app.logger import get_logger

log = get_logger("data_store")


def _conn():
    c = psycopg2.connect(
        host=settings.db_host, port=settings.db_port,
        dbname=settings.db_name, user=settings.db_user,
        password=settings.db_password,
    )
    register_vector(c)
    return c


def index_all(force: bool = False) -> int:
    conn = _conn()
    try:
        with conn.cursor() as cur:
            if not force:
                cur.execute("SELECT COUNT(*) FROM embeddings")
                count = cur.fetchone()[0]
                if count > 0:
                    log.info(f"data_store: already indexed ({count} chunks)")
                    return count

            engine = get_engine()
            with engine.connect() as db_conn:
                chunks = build_all_chunks(db_conn)

            if not chunks:
                log.warning("data_store: no chunks — DB bo'shmi?")
                return 0

            if force:
                cur.execute("TRUNCATE embeddings")

            rows = [
                (c.id, c.text, psycopg2.extras.Json(c.metadata), f"[{','.join(str(x) for x in embed(c.text))}]")
                for c in chunks
            ]
            cur.executemany(
                """INSERT INTO embeddings (id, text, metadata, embedding)
                   VALUES (%s, %s, %s, %s::vector)
                   ON CONFLICT (id) DO UPDATE
                   SET text=EXCLUDED.text,
                       metadata=EXCLUDED.metadata,
                       embedding=EXCLUDED.embedding""",
                rows,
            )
            conn.commit()
    finally:
        conn.close()

    log.info(f"data_store: indexed {len(chunks)} chunks")
    return len(chunks)


def search(question: str, n_results: int = 10) -> str:
    q_vec = embed(question)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT text, metadata FROM embeddings ORDER BY embedding <=> %s::vector LIMIT %s",
                (q_vec, n_results),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        return ""

    top_types = [r[1].get("type") if r[1] else None for r in rows]
    log.info(f"data_store: {len(rows)} chunks — types: {top_types}")
    return "\n\n".join(r[0] for r in rows)
