"""Tests for auth middleware"""

import pytest
import jwt
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone
from starlette.requests import Request
from starlette.responses import Response

from atlas_shared_app.middlewares.auth_middleware import AuthMiddleware
from atlas_shared_app.settings.atlas_identity_settings import AtlasIdentitySettings
from atlas_shared_app.entities import AppEnum, UserRole


@pytest.fixture
def mock_app():
    """Create a mock app"""
    return MagicMock()


@pytest.fixture
def mock_settings():
    """Create mock settings with default RSA keys"""
    return AtlasIdentitySettings(
        base_url="https://api.example.com",
        timeout=30.0,
        public_paths=["/health", "/docs", "/openapi.json"],
    )


@pytest.fixture
def mock_settings_no_public_paths():
    """Create mock settings without public paths"""
    return AtlasIdentitySettings(
        base_url="https://api.example.com",
        timeout=30.0,
        public_paths=[],
    )


@pytest.fixture
def jwt_private_key(mock_settings):
    """JWT private key for signing tokens"""
    return mock_settings.secret_jwt_private_key.get_secret_value()


@pytest.fixture
def valid_token(jwt_private_key):
    """Create a valid JWT token"""
    payload = {
        "user_id": "USER001",
        "login_id": "testuser",
        "user_name": "Test User",
        "user_status": "ACTIVE",
        "email": "test@example.com",
        "phone": "+1234567890",
        "internal": True,
        "client_id": "CLIENT001",
        "client_name": "Test Client",
        "roles": {
            AppEnum.ATLAS_APP_IDENTITY: UserRole.ADMIN,
        },
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, jwt_private_key, algorithm="RS256")


@pytest.fixture
def expired_token(jwt_private_key):
    """Create an expired JWT token"""
    payload = {
        "user_id": "USER001",
        "user_name": "Test User",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    return jwt.encode(payload, jwt_private_key, algorithm="RS256")


@pytest.fixture
def mock_request():
    """Create a mock request"""
    request = MagicMock(spec=Request)
    request.url = MagicMock()
    request.url.path = "/api/users"
    request.headers = MagicMock()
    request.headers.get = MagicMock(return_value=None)
    request.state = MagicMock()
    return request


def test_auth_middleware_init(mock_app, mock_settings):
    """Test AuthMiddleware initialization"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    assert middleware.user_service is not None
    assert middleware.public_paths == ["/health", "/docs", "/openapi.json"]


def test_auth_middleware_init_no_public_paths(mock_app, mock_settings_no_public_paths):
    """Test AuthMiddleware initialization without public paths"""
    middleware = AuthMiddleware(mock_app, mock_settings_no_public_paths)
    assert middleware.public_paths == []


@pytest.mark.asyncio
async def test_dispatch_public_path(mock_app, mock_settings, mock_request):
    """Test dispatch skips auth for public paths"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    mock_request.url.path = "/health"

    expected_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 200
    assert mock_request.state.user is None
    call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_dispatch_public_path_prefix(mock_app, mock_settings, mock_request):
    """Test dispatch skips auth for paths starting with public path prefix"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    mock_request.url.path = "/docs/swagger"

    expected_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 200
    assert mock_request.state.user is None


@pytest.mark.asyncio
async def test_dispatch_valid_token(mock_app, mock_settings, mock_request, valid_token):
    """Test dispatch with valid token sets user on request state"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    mock_request.headers.get = MagicMock(return_value=f"Bearer {valid_token}")

    expected_response = Response(content="OK", status_code=200)
    call_next = AsyncMock(return_value=expected_response)

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 200
    assert mock_request.state.user is not None
    assert mock_request.state.user.user_id == "USER001"
    call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_dispatch_expired_token(mock_app, mock_settings, mock_request, expired_token):
    """Test dispatch with expired token returns 401"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    mock_request.headers.get = MagicMock(return_value=f"Bearer {expired_token}")

    call_next = AsyncMock()

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 401
    assert b"Token has expired" in response.body
    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_dispatch_invalid_token(mock_app, mock_settings, mock_request):
    """Test dispatch with invalid token returns 401"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    mock_request.headers.get = MagicMock(return_value="Bearer invalid_token")

    call_next = AsyncMock()

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 401
    assert b"Invalid token" in response.body
    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_dispatch_invalid_header_format(mock_app, mock_settings, mock_request):
    """Test dispatch with invalid Authorization header format returns 401"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    mock_request.headers.get = MagicMock(return_value="InvalidFormat token")

    call_next = AsyncMock()

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 401
    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_dispatch_no_auth_header(mock_app, mock_settings, mock_request):
    """Test dispatch without Authorization header returns 401"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    mock_request.headers.get = MagicMock(return_value=None)

    call_next = AsyncMock()

    response = await middleware.dispatch(mock_request, call_next)

    assert response.status_code == 401
    assert b"Access token is missing" in response.body
    call_next.assert_not_called()


def test_is_public_path_exact_match(mock_app, mock_settings):
    """Test _is_public_path with exact match"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    assert middleware._is_public_path("/health") is True
    assert middleware._is_public_path("/docs") is True
    assert middleware._is_public_path("/openapi.json") is True


def test_is_public_path_prefix_match(mock_app, mock_settings):
    """Test _is_public_path with prefix match"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    assert middleware._is_public_path("/health/check") is True
    assert middleware._is_public_path("/docs/swagger") is True


def test_is_public_path_no_match(mock_app, mock_settings):
    """Test _is_public_path with no match"""
    middleware = AuthMiddleware(mock_app, mock_settings)
    assert middleware._is_public_path("/api/users") is False
    assert middleware._is_public_path("/private") is False


def test_is_public_path_empty_list(mock_app, mock_settings_no_public_paths):
    """Test _is_public_path with empty public paths list"""
    middleware = AuthMiddleware(mock_app, mock_settings_no_public_paths)
    assert middleware._is_public_path("/health") is False
    assert middleware._is_public_path("/api/users") is False


