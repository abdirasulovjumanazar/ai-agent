import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

_fmt = "%(asctime)s | %(levelname)-5s | %(message)s"
_datefmt = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(_fmt, _datefmt))

    # File — har kuni yangi fayl
    file_handler = TimedRotatingFileHandler(
        logs_dir / "agent.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_fmt, _datefmt))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
