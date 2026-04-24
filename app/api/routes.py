from fastapi import APIRouter, HTTPException
from app.schemas.models import AskRequest, AskResponse
from app.agent.agent import run_agent
from app.logger import get_logger

router = APIRouter()
log = get_logger("routes")


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    log.info(f"question: \"{request.question}\"")
    try:
        result = run_agent(request.question)
        log.info(f"answer: \"{result['answer'][:80]}\"")
        return AskResponse(**result)
    except ValueError as e:
        log.warning(f"blocked: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"error: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
