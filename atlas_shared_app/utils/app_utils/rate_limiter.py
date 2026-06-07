from fastapi import FastAPI, status
from fastapi_throttle import RateLimiter
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ...settings import AtlasThrottlingSettings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that applies both global and per-IP rate limiting."""

    def __init__(self, app, global_limiter: RateLimiter, ip_limiter: RateLimiter):
        super().__init__(app)
        self.global_limiter = global_limiter
        self.ip_limiter = ip_limiter

    async def dispatch(self, request: Request, call_next):
        dummy_response = Response("")
        client_ip = request.client.host if request.client else "unknown"

        # Check global limit first
        try:
            await self.global_limiter(request, dummy_response)
        except Exception:
            logger.warning(
                "Global rate limit exceeded: ip={}, path={}",
                client_ip,
                request.url.path
            )
            # Rate limit exceeded - return 429
            return Response(
                content="Global rate limit exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": "1"}
            )

        # Check per-IP limit
        try:
            await self.ip_limiter(request, dummy_response)
        except Exception:
            logger.warning(
                "IP rate limit exceeded: ip={}, path={}",
                client_ip,
                request.url.path
            )
            # Rate limit exceeded - return 429
            return Response(
                content="IP rate limit exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": "1"}
            )

        # Both checks passed, proceed with request
        response = await call_next(request)

        # Copy rate limit headers to the actual response
        if "X-RateLimit-Limit" in dummy_response.headers:
            response.headers["X-RateLimit-Limit"] = dummy_response.headers["X-RateLimit-Limit"]
            response.headers["X-RateLimit-Remaining"] = dummy_response.headers["X-RateLimit-Remaining"]

        return response


def setup_throttling(app: FastAPI, settings: AtlasThrottlingSettings):
    """
    Setup rate limiting middleware for FastAPI app using fastapi-throttle.

    Usage:
        from fastapi import FastAPI
        from atlas_shared_app.utils.app_utils.rate_limiter import setup_throttling
        from atlas_shared_app.settings.atlas_throttling_settings import AtlasThrottlingSettings

        app = FastAPI()
        setup_throttling(app, AtlasThrottlingSettings())

    Alternative - apply to specific routes:
        from atlas_shared_app.utils.app_utils.rate_limiter import global_limiter, ip_limiter

        @app.get("/", dependencies=[Depends(global_limiter), Depends(ip_limiter)])
        async def root():
            return {"message": "Hello"}
    """

    # Global rate limiter: requests/second total across all IPs
    global_limiter = RateLimiter(
        times=settings.global_limit_per_second,
        seconds=1,
        key_func=lambda _: "global",  # Same key for all requests = global limit
        add_headers=True
    )

    # Per-IP rate limiter: requests/second per IP
    ip_limiter = RateLimiter(
        times=settings.ip_limit_per_second,
        seconds=1,
        key_func=lambda req: req.client.host if req.client else "unknown",  # Per-IP limit
        add_headers=False
    )

    # Add middleware with both limiters
    app.add_middleware(
        RateLimitMiddleware,
        global_limiter=global_limiter,
        ip_limiter=ip_limiter
    )
