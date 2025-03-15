# Logging configuration

import logging
import sys

from config.settings import settings


def setup_logging(file_name: str = "MaccabipediaCalendar") -> logging.Logger:
    """Configure logging for the application."""
    logger = logging.getLogger(file_name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(settings.PYTHON_LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(settings.PYTHON_LOG_LEVEL)

    return logger
