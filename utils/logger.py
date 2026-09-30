"""Logger module for Air Canvas AI."""

import logging
import sys

_logger_initialized = False


def get_logger(name: str = "air_canvas_ai") -> logging.Logger:
    """Get or configure logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger
