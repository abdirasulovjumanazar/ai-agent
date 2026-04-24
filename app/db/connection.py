from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from app.config import settings

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = (
            f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


