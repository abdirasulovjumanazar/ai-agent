import time
from app.vector.query_store import search as cache_search, add as cache_add
from app.vector.data_store import search as data_search
from app.agent.sql_gen import answer_from_context
from app.agent.history import get_history, save_messages
from app.logger import get_logger

log = get_logger("agent")


def run_agent(question: str, session_id: str) -> dict:
    t0 = time.perf_counter()
    log.info(f"{'─'*55}")
    log.info(f"QUESTION: {question}  session={session_id[:8]}…")

    # 1. Semantic cache
    try:
        cached = cache_search(question)
    except Exception as e:
        log.warning(f"query_store search failed: {e}")
        cached = None

    if cached:
        save_messages(session_id, question, cached["answer"])
        log.info(f"VECTOR CACHE HIT | {time.perf_counter() - t0:.2f}s")
        log.info(f"{'─'*55}")
        return cached

    # 2. Chat tarixi
    history = get_history(session_id)

    # 3. Vector search
    context = data_search(question, n_results=10)

    # 4. Gemini
    answer = answer_from_context(question, context, history)

    out = {"answer": answer, "query_used": None, "raw_data": None}

    # 5. Cache va tarixga saqlash
    try:
        cache_add(question, out)
    except Exception as e:
        log.warning(f"query_store save failed: {e}")

    save_messages(session_id, question, answer)

    log.info(f"TOTAL: {time.perf_counter() - t0:.2f}s")
    log.info(f"{'─'*55}")
    return out
