import sys
from pathlib import Path
from loguru import logger
from ..config.settings import settings


def setup_logger():
    logger.remove()
    
    log_path = Path(settings.logging.log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    if settings.logging.log_format.lower() == "json":
        file_log_format = (
            '{{'
            '"timestamp": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level}", '
            '"module": "{module}", '
            '"function": "{function}", '
            '"line": {line}, '
            '"message": "{message}"'
            '}}'
        )
    else:
        file_log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
    
    console_log_format = (
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=console_log_format,
        level=settings.logging.log_level,
        colorize=True,
        filter=lambda record: record["level"].no >= logger.level("INFO").no,
    )
    
    logger.add(
        log_path,
        format=file_log_format,
        level=settings.logging.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info("Logger initialized successfully")