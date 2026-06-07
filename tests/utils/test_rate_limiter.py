"""Tests for rate limiter middleware"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from atlas_shared_app.utils.app_utils.rate_limiter import RateLimitMiddleware, setup_throttling
from atlas_shared_app.settings.atlas_throttling_settings import AtlasThrottlingSettings


@pytest.fixture
def mock_app():
    """Create a mock FastAPI app"""
    return MagicMock()


@pytest.fixture
def mock_request():
    """Create a mock request"""
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    return request


@pytest.fixture
def mock_global_limiter():
    """Create a mock global limiter"""
    return AsyncMock()


@pytest.fixture
def mock_ip_limiter():
    """Create a mock IP limiter"""
    return AsyncMock()


def test_rate_limit_middleware_init(mock_app, mock_global_limiter, mock_ip_limiter):
    """Test RateLimitMiddleware initialization"""
    middleware = RateLimitMiddleware(mock_app, mock_global_limiter, mock_ip_limiter)
    assert middleware.global_limiter == mock_global_limiter
    assert middleware.ip_limiter == mock_ip_limiter


@pytest.mark.asyncio
async def test_rate_limit_middleware_dispatch_success(mock_app, mock_request, mock_global_limiter, mock_ip_limiter):
    """Test successful request through rate limit middleware"""
    middleware = RateLimitMiddleware(mock_app, mock_global_limiter, mock_ip_limiter)

    # Mock call_next to return a response
    expected_response = Response(content="Success", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 200
    mock_global_limiter.assert_called_once()
    mock_ip_limiter.assert_called_once()
    call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_rate_limit_middleware_global_limit_exceeded(mock_app, mock_request, mock_ip_limiter):
    """Test request rejected when global limit exceeded"""
    mock_global_limiter = AsyncMock(side_effect=Exception("Rate limit exceeded"))
    middleware = RateLimitMiddleware(mock_app, mock_global_limiter, mock_ip_limiter)

    call_next = AsyncMock()

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 429
    assert b"Global rate limit exceeded" in response.body
    assert response.headers.get("Retry-After") == "1"
    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limit_middleware_ip_limit_exceeded(mock_app, mock_request, mock_global_limiter):
    """Test request rejected when IP limit exceeded"""
    mock_ip_limiter = AsyncMock(side_effect=Exception("Rate limit exceeded"))
    middleware = RateLimitMiddleware(mock_app, mock_global_limiter, mock_ip_limiter)

    call_next = AsyncMock()

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 429
    assert b"IP rate limit exceeded" in response.body
    assert response.headers.get("Retry-After") == "1"
    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limit_middleware_copies_headers(mock_app, mock_request, mock_global_limiter, mock_ip_limiter):
    """Test that rate limit headers are copied to response"""
    middleware = RateLimitMiddleware(mock_app, mock_global_limiter, mock_ip_limiter)

    # Make global limiter add headers to the dummy response
    async def limiter_with_headers(request, response):
        response.headers["X-RateLimit-Limit"] = "1000"
        response.headers["X-RateLimit-Remaining"] = "999"

    mock_global_limiter.side_effect = limiter_with_headers

    expected_response = Response(content="Success", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    response = await middleware.dispatch(mock_request, call_next)

    assert response.headers.get("X-RateLimit-Limit") == "1000"
    assert response.headers.get("X-RateLimit-Remaining") == "999"


def test_setup_throttling():
    """Test setup_throttling adds middleware to app"""
    app = FastAPI()

    # Count middleware before
    middleware_count_before = len(app.user_middleware)

    throttling_settings = AtlasThrottlingSettings()
    setup_throttling(app, throttling_settings)

    # Check that middleware was added
    assert len(app.user_middleware) > middleware_count_before


def test_setup_throttling_custom_limits():
    """Test setup_throttling with custom limits"""
    app = FastAPI()

    throttling_settings = AtlasThrottlingSettings(
        global_limit_per_second=500,
        ip_limit_per_second=50
    )
    setup_throttling(app, throttling_settings)

    # Verify middleware was added (we can't easily verify the limits without more introspection)
    assert len(app.user_middleware) > 0
