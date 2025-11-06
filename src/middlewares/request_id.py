# middlewares/request_id.py
import uuid
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from common.context import request_id_ctx

logger = logging.getLogger(__name__)
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Lấy request_id từ header client gửi, nếu không thì tự sinh UUID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = request_id_ctx.set(request_id)
        request.state.request_id = request_id
        method = request.method
        path = request.url.path
        try:
            start_time = time.time()
            logger.info(f"[Request] {method} {path}")
            response:Response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            status_code = response.status_code
            logger.info(f"[Response] {method} {path} status={status_code} duration={duration:.2f}ms")
            return response
        finally:
            request_id_ctx.reset(token)
