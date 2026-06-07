import sys
from loguru import logger

from ...settings import AtlasLoggingSettings
from .logging_context import context_filter


def setup_logging(settings: AtlasLoggingSettings, is_local: bool = False):
    logger.remove()
    if is_local:
        logger.add(
            sys.stdout,
            colorize=True,
            backtrace=settings.backtrace,
            diagnose=settings.diagnose,
            level=settings.level,
            format=settings.format,
            filter=context_filter,
        )

    logger.add(
        settings.log_file,
        rotation=settings.rotation,
        retention=settings.retention,
        backtrace=settings.backtrace,
        diagnose=settings.diagnose,
        level=settings.level,
        format=settings.format,
        filter=context_filter,
    )
