import re
import time
from sqlalchemy import text
from app.db.connection import get_engine
from app.logger import get_logger

log = get_logger("executor")


def _extract_tables(sql: str) -> str:
    tables = re.findall(r"(?:FROM|JOIN)\s+([a-zA-Z_]\w*)", sql, re.IGNORECASE)
    return ", ".join(dict.fromkeys(tables)) if tables else "unknown"


def execute_query(sql: str) -> list[dict]:
    t0 = time.perf_counter()
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

    tables = _extract_tables(sql)
    log.info(f"[3/4] DB FETCH   → table: {tables} | rows: {len(rows)} | {time.perf_counter() - t0:.3f}s")
    return rows
