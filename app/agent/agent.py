import time
from app.db.executor import execute_query
from app.db.reducer import reduce_schema
from app.agent.sql_gen import classify_and_generate, results_to_answer
from app.logger import get_logger

log = get_logger("agent")

# Oddiy in-memory cache: { normalized_question: result }
_cache: dict[str, dict] = {}


def _normalize(q: str) -> str:
    return q.strip().lower()


def run_agent(question: str) -> dict:
    t0 = time.perf_counter()
    key = _normalize(question)

    # Cache dan qaytarish
    if key in _cache:
        log.info(f"{'─'*55}")
        log.info(f"QUESTION: {question}")
        log.info("CACHE HIT — skipping Gemini")
        log.info(f"{'─'*55}")
        return _cache[key]

    log.info(f"{'─'*55}")
    log.info(f"QUESTION: {question}")

    schema = reduce_schema(question)
    result = classify_and_generate(question, schema)

    if result["type"] == "general":
        out = {"answer": result["answer"], "query_used": None, "raw_data": None}
        _cache[key] = out
        log.info(f"TOTAL: {time.perf_counter() - t0:.2f}s")
        log.info(f"{'─'*55}")
        return out

    sql = result["sql"]
    rows = execute_query(sql)
    answer = results_to_answer(question, sql, rows)

    out = {"answer": answer, "query_used": sql, "raw_data": rows}
    _cache[key] = out

    log.info(f"TOTAL: {time.perf_counter() - t0:.2f}s")
    log.info(f"{'─'*55}")
    return out
