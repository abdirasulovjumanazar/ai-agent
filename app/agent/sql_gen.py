import re
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import settings
from app.logger import get_logger

log = get_logger("sql_gen")

SMART_PROMPT = PromptTemplate.from_template(
    """You are a helpful AI assistant with access to a PostgreSQL database. You support any language — always reply in the same language the user used.

Database schema:
{schema}

User question: {question}

Instructions:
- If the question requires database data, respond with ONLY a valid PostgreSQL SELECT query (no explanation, no markdown, no backticks).
- If the question can be answered without the database (greetings, general questions, etc.), respond with ONLY the plain text answer starting with "ANSWER:" in the user's language.
- When filtering by name, always use ILIKE '%value%' instead of exact = match.
- Always use SELECT DISTINCT to avoid duplicate rows in results.

Response:"""
)

ANSWER_PROMPT = PromptTemplate.from_template(
    """You are a helpful assistant. Answer the user's question based on the database query results.

User question: {question}
SQL query used: {sql}
Query results: {results}

Give a clear, concise natural language answer."""
)


def _make_llm(temperature: float = 0) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=temperature,
        max_retries=3,
    )


def classify_and_generate(question: str, schema: str) -> dict:
    t0 = time.perf_counter()
    chain = SMART_PROMPT | _make_llm(0)
    result = chain.invoke({"question": question, "schema": schema})
    content = result.content.strip()
    elapsed = time.perf_counter() - t0

    if content.upper().startswith("ANSWER:"):
        answer = content[7:].strip()
        log.info(f"[1/1] CLASSIFY+ANSWER → general | {elapsed:.2f}s")
        return {"type": "general", "answer": answer}

    sql = re.sub(r"^```(?:sql)?\s*", "", content, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql).strip()
    log.info(f"[1/2] CLASSIFY+SQL → {sql[:60]}{'...' if len(sql) > 60 else ''} | {elapsed:.2f}s")
    return {"type": "sql", "sql": sql}


def results_to_answer(question: str, sql: str, results: list[dict]) -> str:
    t0 = time.perf_counter()
    chain = ANSWER_PROMPT | _make_llm(0.2)
    result = chain.invoke({"question": question, "sql": sql, "results": str(results)})
    answer = result.content.strip()
    log.info(f"[2/2] ANSWER GEN  → {answer[:60]}{'...' if len(answer) > 60 else ''} | {time.perf_counter() - t0:.2f}s")
    return answer
