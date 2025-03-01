# Logging configuration

import logging
import os
import sys


def setup_logging(file_name: str = "MaccabipediaCalendar") -> logging.Logger:
    """Configure logging for the application."""
    logger = logging.getLogger(file_name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                os.getenv(
                    "PYTHON_LOG_FORMAT",
                    "%(asctime)s | %(levelname)s | %(process)d | %(name)s | %(filename)s:%(lineno)d | %(message)s",
                )
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
