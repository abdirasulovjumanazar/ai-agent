from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.api.routes import router
from app.logger import get_logger

log = get_logger("main")

app = FastAPI(
    title="AI Database Agent",
    description="Ask questions in natural language — get answers from your PostgreSQL database.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

_html = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
log.info("AI Agent started — http://127.0.0.1:8000")


@app.get("/", include_in_schema=False)
def root():
    return HTMLResponse(content=_html)


@app.get("/health")
def health():
    return {"status": "ok"}
