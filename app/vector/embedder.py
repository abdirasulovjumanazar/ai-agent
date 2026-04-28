from google import genai
from app.config import settings

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def embed(text: str) -> list[float]:
    """Matnni vektorga aylantiradi (gemini-embedding-001, 3072-dim)."""
    result = _get_client().models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values
