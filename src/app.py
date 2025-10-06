from fastapi import FastAPI
from common.setting import get_settings
from api.v1 import api_v1_router
from middlewares.request_id import RequestIDMiddleware
import logging

setting = get_settings()
logger = logging.getLogger(__name__)

# Khởi tạo FastAPI app
app = FastAPI(title=get_settings().SERVICE_NAME)

app.add_middleware(RequestIDMiddleware)

app.include_router(api_v1_router)

@app.get("/health")
async def health():
    logger.info("Health check OK")
    return {"status": "ok"}
