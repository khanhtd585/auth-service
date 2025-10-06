import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
import logging
import asyncio

from src.common.setting import get_settings
from src.common.logging import setup_logging
from src.db.database import get_database

logger = logging.getLogger(__name__)
setting = get_settings()

def pre_check():
    # check db connection
    get_database()
    logger.info("✅ Database connection success")

if __name__ == "__main__":
    setup_logging(log_level="INFO", 
                  log_dir=f"./log/{setting.SERVICE_NAME}", 
                  log_file=f"{setting.SERVICE_NAME}.log")
    
    pre_check()
    
    uvicorn.run('src.app:app', 
                host=setting.HOST, 
                port=setting.PORT,
                reload=setting.DEBUG_MODE,
                log_config=None,
                log_level="info"
                )