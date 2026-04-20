# education-hub-core/app/util/logger.py
import logging
from pathlib import Path
import sys

from loguru import logger

from app.config.config import settings


LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


class InterceptHandler(logging.Handler):
    """
    Standard Python logging handler that redirects logs to Loguru.
    This allows capturing logs from other libraries (e.g.).
    """

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger():
    """
    Configures Loguru sinks and overrides the standard logging configuration.
    """
    logger.remove()

    if settings.LOG_JSON_FORMAT:
        logger.add(sys.stdout, serialize=True, level=settings.LOG_LEVEL)
    else:
        logger.add(
            sys.stdout,
            colorize=True,
            format=LOG_FORMAT,
            level=settings.LOG_LEVEL,
        )

    if settings.ENV != "testing":
        LOG_DIR = Path("logs")
        LOG_DIR.mkdir(exist_ok=True)

        logger.add(
            LOG_DIR / "app_{time:YYYY-MM-DD}.log",
            rotation="10 MB",
            retention="10 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            encoding="utf-8",
            enqueue=True,
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for name in logging.root.manager.loggerDict:
        _log = logging.getLogger(name)
        _log.handlers = []
        _log.propagate = True
    logging.getLogger().setLevel(settings.LOG_LEVEL)


setup_logger()

__all__ = ["logger"]
