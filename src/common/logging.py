import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from common.context import request_id_ctx


class RenameLoggerFilter(logging.Filter):
    """
    Đổi tên logger uvicorn.error -> uvicorn.server
    """
    def filter(self, record):
        if record.name == "uvicorn.error":
            record.name = "uvicorn.server"
        return True

class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get("-")
        return True


def setup_logging(log_level=logging.INFO, log_dir="logs", log_file="app.log"):
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | [req=%(request_id)s] %(message)s"

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.addFilter(RenameLoggerFilter())
    console_handler.addFilter(RequestIDFilter())

    config = {
        "level": log_level,
        "format": log_format,
        "handlers": [console_handler],
    }

    if log_dir and log_file:
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_file)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.addFilter(RenameLoggerFilter())
        file_handler.addFilter(RequestIDFilter())
        config["handlers"].append(file_handler)

    logging.basicConfig(**config)

    # Reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.getLogger(__name__).info("✅ Logging initialized. Logs will be saved at %s", log_file)
