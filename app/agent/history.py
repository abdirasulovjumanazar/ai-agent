import psycopg2
from app.config import settings
from app.logger import get_logger

log = get_logger("history")


def _conn():
    return psycopg2.connect(
        host=settings.db_host, port=settings.db_port,
        dbname=settings.db_name, user=settings.db_user,
        password=settings.db_password,
    )


def get_history(session_id: str, limit: int = 6) -> str:
    """Oxirgi N ta xabarni 'User: ...\nAI: ...\n---' formatida qaytaradi."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT role, content FROM chat_history
                   WHERE session_id = %s
                   ORDER BY created_at DESC
                   LIMIT %s""",
                (session_id, limit),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        return ""

    pairs = []
    rows = list(reversed(rows))
    for i in range(0, len(rows) - 1, 2):
        user_msg = rows[i][1]     if rows[i][0]   == "user"      else rows[i+1][1]
        ai_msg   = rows[i+1][1]   if rows[i+1][0] == "assistant" else rows[i][1]
        pairs.append(f"User: {user_msg}\nAI: {ai_msg}")

    return "\n---\n".join(pairs)


def save_messages(session_id: str, question: str, answer: str) -> None:
    """Foydalanuvchi savoli va AI javobini DB ga saqlaydi."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chat_history (session_id, role, content) VALUES (%s, %s, %s)",
                [
                    (session_id, "user",      question),
                    (session_id, "assistant", answer),
                ],
            )
            conn.commit()
    finally:
        conn.close()
    log.info(f"history: saved session={session_id[:8]}…")
