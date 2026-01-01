"""
Logging configuration using loguru
"""
import sys
from loguru import logger
from .config import settings


def setup_logging():
    """Configure application logging"""
    logger.remove()  # Remove default handler
    
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # Add file logging for production
    if settings.ENV == "production":
        logger.add(
            "logs/evrag_{time}.log",
            rotation="500 MB",
            retention="10 days",
            level="INFO",
        )
    
    return logger


log = setup_logging()

