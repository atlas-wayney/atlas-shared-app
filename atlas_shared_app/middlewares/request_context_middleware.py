"""
Middleware for capturing and propagating request context for logging.
"""
from typing import Callable
from uuid import uuid4

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.logging_utils import clear_request_context, set_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that captures request context (request_id, user_id, client_id)
    and makes it available for logging throughout the request lifecycle.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # Generate or extract request ID from header
        request_id = request.headers.get("X-Request-ID") or str(uuid4())

        # Get user info from request state (set by AuthMiddleware)
        user = getattr(request.state, "user", None)
        user_id = user.user_id if user else None
        client_id = user.client_id if user else None

        # Set context for this request
        set_request_context(
            request_id=request_id,
            user_id=user_id,
            client_id=client_id
        )

        # Log request start
        logger.info(
            "Request started: {} {}",
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)

            # Log request completion
            logger.info(
                "Request completed: {} {} -> {}",
                request.method,
                request.url.path,
                response.status_code
            )

            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as e:
            logger.error(
                "Request failed: {} {} - {}",
                request.method,
                request.url.path,
                str(e)
            )
            raise
        finally:
            clear_request_context()
