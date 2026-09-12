"""Logging configuration"""

import logging
import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure structured logging with loguru"""
    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
    )

    # Add file handler for production
    if settings.APP_ENVIRONMENT == "production":
        logger.add(
            "logs/trustchain.log",
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="500 MB",
            retention="10 days",
        )


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
