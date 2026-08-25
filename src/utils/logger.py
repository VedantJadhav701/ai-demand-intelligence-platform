"""
Structured logging configuration for the AI Demand Intelligence Platform.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "demand_intelligence",
    log_level: str = "INFO",
    log_file: Optional[str | Path] = None,
) -> logging.Logger:
    """
    Configures and returns a logger instance with formatted console and optional file handlers.

    Args:
        name: Name of the logger instance.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to a file where logs should be saved.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def get_logger(name: str = "demand_intelligence") -> logging.Logger:
    """
    Retrieves or creates a logger instance.

    Args:
        name: Name of the logger instance.

    Returns:
        logging.Logger: Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
