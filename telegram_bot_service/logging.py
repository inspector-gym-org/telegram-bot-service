from pydantic import BaseModel

from .config import settings


class LogConfig(BaseModel):
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "format": settings.log_format,
            "datefmt": settings.log_date_format,
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers = {
        "service": {
            "handlers": ["default"],
            "level": settings.log_level,
        },
    }
