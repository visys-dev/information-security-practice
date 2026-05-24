import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.audit.logger import log_event
from app.database import SessionLocal


class AuditMiddleware(BaseHTTPMiddleware):
    """Automatically log security-relevant HTTP requests."""

    SKIP_PATHS = {"/docs", "/openapi.json", "/redoc", "/favicon.ico"}
    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        should_log = request.method in self.WRITE_METHODS or response.status_code >= 400
        if not should_log:
            return response

        ip = request.client.host if request.client else "unknown"
        if response.status_code >= 500:
            status = "error"
        elif response.status_code in (401, 403):
            status = "failure"
        else:
            status = "success"

        db = SessionLocal()
        try:
            log_event(
                db=db,
                action=f"http_{request.method.lower()}",
                status=status,
                ip_address=ip,
                http_method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                details={"duration_ms": duration_ms},
            )
        finally:
            db.close()

        return response

