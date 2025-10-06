# context.py
import contextvars

# Context variable lưu request_id cho mỗi request
request_id_ctx = contextvars.ContextVar("request_id", default="-")
