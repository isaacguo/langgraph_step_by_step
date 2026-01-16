import structlog
import logging
import sys
from logging.handlers import RotatingFileHandler

def configure_logging(log_level: str = "INFO", log_file: str = "/var/log/app/safety.log"):
    """
    Configure structured logging.
    """
    # Standard library configuration
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        try:
            handlers.append(RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5))
        except IOError:
            pass # Fallback to stdout if file not writable

    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=handlers
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()

logger = configure_logging()
