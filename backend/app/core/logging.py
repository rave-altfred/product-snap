import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings


def setup_logging():
    """Configure structured JSON logging."""
    logger = logging.getLogger()
    
    logHandler = logging.StreamHandler(sys.stdout)
    
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp",
            "name": "logger"
        }
    )
    
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    return logger


# Request ID context
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_var.get()


def set_request_id(request_id: str):
    """Set request ID in context."""
    request_id_var.set(request_id)
