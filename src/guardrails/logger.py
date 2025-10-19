"""Logging utilities for the guardrails SDK."""

import logging

LOGGER_NAME = "guardrails"


def get_logger() -> logging.Logger:
    """Return a shared logger configured with sensible defaults."""
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


guard_logger = get_logger()

