# middlewares/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from common.context import request_id_ctx

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Lấy request_id từ header client gửi, nếu không thì tự sinh UUID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid1()))
        token = request_id_ctx.set(request_id)
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            return response
        finally:
            request_id_ctx.reset(token)
