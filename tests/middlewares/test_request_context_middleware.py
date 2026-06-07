"""Tests for RequestContextMiddleware"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from starlette.responses import Response

from atlas_shared_app.middlewares.request_context_middleware import RequestContextMiddleware


@pytest.fixture
def mock_app():
    """Create a mock app"""
    return MagicMock()


@pytest.fixture
def mock_request():
    """Create a mock request"""
    request = MagicMock()
    request.method = "GET"
    request.url = MagicMock()
    request.url.path = "/api/test"
    request.headers = MagicMock()
    request.headers.get = MagicMock(return_value=None)
    request.state = MagicMock()
    # No user by default
    del request.state.user
    return request


@pytest.fixture
def mock_request_with_user():
    """Create a mock request with user"""
    request = MagicMock()
    request.method = "POST"
    request.url = MagicMock()
    request.url.path = "/api/users"
    request.headers = MagicMock()
    request.headers.get = MagicMock(return_value=None)
    request.state = MagicMock()
    request.state.user = MagicMock()
    request.state.user.user_id = "USER001"
    request.state.user.client_id = "CLIENT001"
    return request


@pytest.mark.asyncio
async def test_dispatch_success_without_user(mock_app, mock_request):
    """Test middleware dispatch without user info"""
    middleware = RequestContextMiddleware(mock_app)

    expected_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    with patch("atlas_shared_app.middlewares.request_context_middleware.set_request_context") as mock_set:
        with patch("atlas_shared_app.middlewares.request_context_middleware.clear_request_context") as mock_clear:
            response = await middleware.dispatch(mock_request, call_next)

            assert response.status_code == 200
            assert "X-Request-ID" in response.headers
            mock_set.assert_called_once()
            mock_clear.assert_called_once()
            call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_dispatch_success_with_user(mock_app, mock_request_with_user):
    """Test middleware dispatch with user info"""
    middleware = RequestContextMiddleware(mock_app)

    expected_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    with patch("atlas_shared_app.middlewares.request_context_middleware.set_request_context") as mock_set:
        with patch("atlas_shared_app.middlewares.request_context_middleware.clear_request_context") as mock_clear:
            response = await middleware.dispatch(mock_request_with_user, call_next)

            assert response.status_code == 200
            mock_set.assert_called_once()
            # Verify user_id and client_id were passed
            call_args = mock_set.call_args
            assert call_args.kwargs["user_id"] == "USER001"
            assert call_args.kwargs["client_id"] == "CLIENT001"


@pytest.mark.asyncio
async def test_dispatch_uses_request_id_header(mock_app, mock_request):
    """Test middleware uses X-Request-ID from header if provided"""
    middleware = RequestContextMiddleware(mock_app)
    mock_request.headers.get = MagicMock(return_value="custom-request-id")

    expected_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    with patch("atlas_shared_app.middlewares.request_context_middleware.set_request_context") as mock_set:
        response = await middleware.dispatch(mock_request, call_next)

        assert response.headers["X-Request-ID"] == "custom-request-id"
        call_args = mock_set.call_args
        assert call_args.kwargs["request_id"] == "custom-request-id"


@pytest.mark.asyncio
async def test_dispatch_generates_request_id(mock_app, mock_request):
    """Test middleware generates request ID if not in header"""
    middleware = RequestContextMiddleware(mock_app)

    expected_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    response = await middleware.dispatch(mock_request, call_next)

    # Should have a generated UUID
    request_id = response.headers["X-Request-ID"]
    assert request_id is not None
    assert len(request_id) == 36  # UUID format


@pytest.mark.asyncio
async def test_dispatch_exception_handling(mock_app, mock_request):
    """Test middleware handles exceptions and clears context"""
    middleware = RequestContextMiddleware(mock_app)

    call_next = AsyncMock(side_effect=ValueError("Test error"))

    with patch("atlas_shared_app.middlewares.request_context_middleware.set_request_context"):
        with patch("atlas_shared_app.middlewares.request_context_middleware.clear_request_context") as mock_clear:
            with pytest.raises(ValueError, match="Test error"):
                await middleware.dispatch(mock_request, call_next)

            # Context should still be cleared even on exception
            mock_clear.assert_called_once()


@pytest.mark.asyncio
async def test_dispatch_logs_request_lifecycle(mock_app, mock_request):
    """Test middleware logs request start and completion"""
    middleware = RequestContextMiddleware(mock_app)

    expected_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    with patch("atlas_shared_app.middlewares.request_context_middleware.logger") as mock_logger:
        await middleware.dispatch(mock_request, call_next)

        # Should log start and completion
        assert mock_logger.info.call_count == 2


@pytest.mark.asyncio
async def test_dispatch_logs_error_on_exception(mock_app, mock_request):
    """Test middleware logs error when exception occurs"""
    middleware = RequestContextMiddleware(mock_app)

    call_next = AsyncMock(side_effect=RuntimeError("Something went wrong"))

    with patch("atlas_shared_app.middlewares.request_context_middleware.logger") as mock_logger:
        with pytest.raises(RuntimeError):
            await middleware.dispatch(mock_request, call_next)

        # Should log the error
        mock_logger.error.assert_called_once()
