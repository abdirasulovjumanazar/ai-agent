import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import settings
from app.logger import get_logger

log = get_logger("sql_gen")

CONTEXT_PROMPT = PromptTemplate.from_template(
    """You are a helpful assistant analyzing database records. Always reply in the same language as the question.

{history_section}Relevant database records:
{context}

User question: {question}

Instructions:
- Answer based only on the provided records and conversation history
- If counting, count precisely from the given records
- If the information is not in the records, say so clearly
- Be concise and direct

Answer:"""
)


def _make_llm(temperature: float = 0) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=temperature,
        max_retries=3,
    )


def answer_from_context(question: str, context: str, history: str = "") -> str:
    """Vector search natijalaridan tabiiy til javob hosil qiladi."""
    t0 = time.perf_counter()
    history_section = (
        f"Previous conversation:\n{history}\n\n" if history else ""
    )
    chain = CONTEXT_PROMPT | _make_llm(0)
    result = chain.invoke({
        "question":        question,
        "context":         context,
        "history_section": history_section,
    })
    answer = result.content.strip()
    log.info(f"ANSWER → {answer[:60]}{'...' if len(answer) > 60 else ''} | {time.perf_counter() - t0:.2f}s")
    return answer
