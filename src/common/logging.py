import os
from common.setting import get_settings

import logging
from common.context import request_id_ctx

class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True

def setup_logging():
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | [req_id=%(request_id)s] | %(message)s"
    log_dir=get_settings().LOG_DIR
    log_file=f"{get_settings().SERVICE_NAME}.log"
    log_path=os.path.join(log_dir, log_file)
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {'standard': {'format': log_format}},
        'filters': {
            'request_id_filter': {
                '()': 'common.logging.RequestIDFilter',
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.WatchedFileHandler',
                'filename': log_path, 
                'level': 'INFO',
                'formatter': 'standard',
                'filters': ['request_id_filter'],
            },
            'console': {
                'class': 'logging.StreamHandler', 
                'level': 'INFO', 
                'formatter': 'standard', 
                'filters': ['request_id_filter'],
                },
        },
        'loggers': {
            'uvicorn': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'uvicorn.error': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': False},
            'uvicorn.access': {'handlers': ['file', 'console'], 'level': 'WARNING', 'propagate': False},
            'sqlalchemy': {'handlers': ['file', 'console'], 'level': 'WARNING', 'propagate': False},
            'sqlalchemy.engine': {'handlers': ['file', 'console'], 'level': 'WARNING', 'propagate': False},
        },
        'root': {'handlers': ['file', 'console'], 'level': 'INFO'},
    }