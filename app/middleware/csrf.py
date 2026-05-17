from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_origins: list[str]):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in SAFE_METHODS:
            origin = request.headers.get("origin")
            referer = request.headers.get("referer")

            if origin and origin not in self.allowed_origins:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF protection: недозволений Origin"},
                )

            if not origin and referer:
                if not any(referer.startswith(item) for item in self.allowed_origins):
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF protection: недозволений Referer"},
                    )

        return await call_next(request)
