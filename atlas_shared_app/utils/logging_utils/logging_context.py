"""
Logging context utilities for request-scoped logging.

Provides context binding for user_id, client_id, and request_id
to enable traceability across log entries.
"""
from contextvars import ContextVar
from typing import Optional
from uuid import uuid4


# Context variables for request-scoped data
_request_context: ContextVar[dict] = ContextVar("request_context", default={})


def get_request_id() -> str:
    """Get the current request ID from context."""
    ctx = _request_context.get()
    return ctx.get("request_id", "-")


def get_user_id() -> Optional[str]:
    """Get the current user ID from context."""
    ctx = _request_context.get()
    return ctx.get("user_id")


def get_client_id() -> Optional[str]:
    """Get the current client ID from context."""
    ctx = _request_context.get()
    return ctx.get("client_id")


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    client_id: Optional[str] = None
) -> None:
    """
    Set the request context for the current async context.

    Args:
        request_id: Unique identifier for the request (generated if not provided)
        user_id: ID of the authenticated user
        client_id: ID of the user's client organization
    """
    ctx = {
        "request_id": request_id or str(uuid4()),
        "user_id": user_id,
        "client_id": client_id,
    }
    _request_context.set(ctx)


def clear_request_context() -> None:
    """Clear the request context."""
    _request_context.set({})


def context_filter(record) -> bool:
    """
    Loguru filter that adds request context to log records.

    This filter injects request_id, user_id, and client_id into the
    'extra' dictionary of each log record for inclusion in log output.
    """
    ctx = _request_context.get()
    record["extra"]["request_id"] = ctx.get("request_id", "-")
    record["extra"]["user_id"] = ctx.get("user_id", "-")
    record["extra"]["client_id"] = ctx.get("client_id", "-")
    return True
