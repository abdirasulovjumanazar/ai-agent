from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager
from app.api.routes import router
from app.vector.data_store import index_all
from app.logger import get_logger

log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Indexing DB into vector store…")
    index_all()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="AI Database Agent",
    description="Ask questions in natural language — get answers from your PostgreSQL database.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

_html_path = Path(__file__).parent / "static" / "index.html"
log.info("AI Agent started — http://127.0.0.1:8001")


@app.get("/", include_in_schema=False)
def root():
    return HTMLResponse(content=_html_path.read_text(encoding="utf-8"))


@app.get("/health")
def health():
    return {"status": "ok"}
