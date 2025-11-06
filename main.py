import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
import logging

from src.common.setting import get_settings
from src.common.logging import setup_logging
from common.context import request_id_ctx
# from src.db.database import get_database

class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True

setting = get_settings()
log_config = setup_logging()

logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    
    uvicorn.run('src.app:app', 
                host=setting.HOST, 
                port=setting.PORT,
                reload=setting.DEBUG_MODE,
                log_config=log_config
                )