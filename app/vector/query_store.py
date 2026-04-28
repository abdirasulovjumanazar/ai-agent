import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector

from app.vector.embedder import embed
from app.config import settings
from app.logger import get_logger

log = get_logger("query_store")

THRESHOLD = 0.15


def _conn():
    c = psycopg2.connect(
        host=settings.db_host, port=settings.db_port,
        dbname=settings.db_name, user=settings.db_user,
        password=settings.db_password,
    )
    register_vector(c)
    return c


def search(question: str) -> dict | None:
    q_vec = embed(question)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT answer, embedding <=> %s::vector AS dist
                   FROM query_cache
                   ORDER BY dist
                   LIMIT 1""",
                (q_vec,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        log.info("query_store: MISS (cache empty)")
        return None

    answer, dist = row
    if dist <= THRESHOLD:
        log.info(f"query_store: HIT  dist={dist:.3f}")
        return answer

    log.info(f"query_store: MISS dist={dist:.3f}")
    return None


def add(question: str, result: dict) -> None:
    vec = embed(question)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            qid = str(abs(hash(question.strip().lower())))
            cur.execute(
                """INSERT INTO query_cache (id, question, answer, embedding)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (id) DO UPDATE
                   SET answer = EXCLUDED.answer,
                       embedding = EXCLUDED.embedding""",
                (qid, question, psycopg2.extras.Json(result), f"[{','.join(str(x) for x in vec)}]"),
            )
            conn.commit()
    finally:
        conn.close()

    log.info(f"query_store: saved '{question[:50]}'")
