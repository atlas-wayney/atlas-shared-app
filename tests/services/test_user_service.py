"""Tests for User service"""

import pytest
import jwt
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta, timezone

import httpx

from atlas_shared_app.entities import UserRole, AppEnum
from atlas_shared_app.entities.atlas_base_enums import SharedEnum, EntityStatus
from atlas_shared_app.shared_services.atlas_user_service import AtlasUserService
from atlas_shared_app.settings.atlas_identity_settings import AtlasIdentitySettings


@pytest.fixture
def mock_settings():
    """Create mock user settings with default RSA keys"""
    return AtlasIdentitySettings(
        base_url="https://api.example.com",
        timeout=30.0
    )


@pytest.fixture
def jwt_private_key(mock_settings):
    """JWT private key for signing tokens"""
    return mock_settings.secret_jwt_private_key.get_secret_value()


@pytest.fixture
def jwt_public_key(mock_settings):
    """JWT public key for verifying tokens"""
    return mock_settings.secret_jwt_public_key.get_secret_value()


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
            AppEnum.ATLAS_APP_NETWORK: UserRole.VIEWER,
        },
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, jwt_private_key, algorithm="RS256")


@pytest.fixture
def expired_token(jwt_private_key):
    """Create an expired JWT token"""
    payload = {
        "user_id": "USER001",
        "user_name": "Test User",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expired
    }
    return jwt.encode(payload, jwt_private_key, algorithm="RS256")


def test_user_service_init(mock_settings):
    """Test AtlasUserService initialization"""
    service = AtlasUserService(mock_settings)
    assert service.base_url == "https://api.example.com"
    assert service.timeout == 30.0
    assert service.algorithm == "RS256"
    assert service.jwt_public_key == mock_settings.secret_jwt_public_key.get_secret_value()
    assert service.jwt_private_key == mock_settings.secret_jwt_private_key.get_secret_value()


def test_user_service_jwt_key_property(mock_settings):
    """Test JWT key property returns public key"""
    service = AtlasUserService(mock_settings)
    assert service.jwt_key == mock_settings.secret_jwt_public_key.get_secret_value()


def test_get_system_user():
    """Test get_system_user returns default system user"""
    user = AtlasUserService.get_system_user()

    assert user.user_id == SharedEnum.SYSTEM
    assert user.user_name == SharedEnum.SYSTEM
    assert user.user_status == EntityStatus.ACTIVE
    assert user.email == ""
    assert user.roles[AppEnum.ATLAS_APP_IDENTITY] == UserRole.ADMIN


def test_get_user_success(mock_settings, valid_token):
    """Test get_user decodes valid token"""
    service = AtlasUserService(mock_settings)

    user = service.get_user(valid_token)

    assert user.user_id == "USER001"
    assert user.user_name == "Test User"
    assert user.email == "test@example.com"
    assert user.internal is True
    assert user.client_id == "CLIENT001"


def test_get_user_expired_token(mock_settings, expired_token):
    """Test get_user raises error for expired token"""
    service = AtlasUserService(mock_settings)

    with pytest.raises(jwt.ExpiredSignatureError):
        service.get_user(expired_token)


def test_get_user_invalid_token(mock_settings):
    """Test get_user raises error for invalid token"""
    service = AtlasUserService(mock_settings)

    with pytest.raises(jwt.InvalidTokenError):
        service.get_user("invalid_token_string")


def test_get_user_optional_success(mock_settings, valid_token):
    """Test get_user_optional returns user for valid token"""
    service = AtlasUserService(mock_settings)

    user = service.get_user_optional(valid_token)

    assert user is not None
    assert user.user_id == "USER001"


def test_get_user_optional_expired_token(mock_settings, expired_token):
    """Test get_user_optional returns None for expired token"""
    service = AtlasUserService(mock_settings)

    user = service.get_user_optional(expired_token)

    assert user is None


def test_get_user_optional_invalid_token(mock_settings):
    """Test get_user_optional returns None for invalid token"""
    service = AtlasUserService(mock_settings)

    user = service.get_user_optional("invalid_token")

    assert user is None


def test_get_user_from_header_success(mock_settings, valid_token):
    """Test get_user_from_header extracts user from Bearer token"""
    service = AtlasUserService(mock_settings)

    user = service.get_user_from_header(f"Bearer {valid_token}")

    assert user.user_id == "USER001"


def test_get_user_from_header_invalid_format(mock_settings):
    """Test get_user_from_header raises error for invalid format"""
    service = AtlasUserService(mock_settings)

    with pytest.raises(ValueError) as exc_info:
        service.get_user_from_header("InvalidHeader token")

    assert "Invalid Authorization header format" in str(exc_info.value)


def test_get_user_from_request_with_valid_token(mock_settings, valid_token):
    """Test get_user_from_request extracts user from request"""
    service = AtlasUserService(mock_settings)

    mock_request = MagicMock()
    mock_request.headers.get.return_value = f"Bearer {valid_token}"

    user = service.get_user_from_request(mock_request)

    assert user.user_id == "USER001"


def test_get_user_from_request_no_auth_header(mock_settings):
    """Test get_user_from_request returns system user when no auth header"""
    service = AtlasUserService(mock_settings)

    mock_request = MagicMock()
    mock_request.headers.get.return_value = None

    user = service.get_user_from_request(mock_request)

    assert user.user_id == SharedEnum.SYSTEM


def test_get_user_from_request_invalid_token(mock_settings):
    """Test get_user_from_request returns system user for invalid token"""
    service = AtlasUserService(mock_settings)

    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer invalid_token"

    user = service.get_user_from_request(mock_request)

    assert user.user_id == SharedEnum.SYSTEM


def test_get_user_from_request_expired_token(mock_settings, expired_token):
    """Test get_user_from_request returns system user for expired token"""
    service = AtlasUserService(mock_settings)

    mock_request = MagicMock()
    mock_request.headers.get.return_value = f"Bearer {expired_token}"

    user = service.get_user_from_request(mock_request)

    assert user.user_id == SharedEnum.SYSTEM


def test_get_user_from_request_invalid_header_format(mock_settings):
    """Test get_user_from_request returns system user for invalid header format"""
    service = AtlasUserService(mock_settings)

    mock_request = MagicMock()
    mock_request.headers.get.return_value = "InvalidFormat token"

    user = service.get_user_from_request(mock_request)

    assert user.user_id == SharedEnum.SYSTEM


def test_get_user_with_default_values(mock_settings, jwt_private_key):
    """Test get_user handles missing optional fields"""
    service = AtlasUserService(mock_settings)

    # Create token with minimal payload
    payload = {
        "user_id": "USER002",
        "login_id": "minimaluser",
        "user_name": "Minimal User",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, jwt_private_key, algorithm="RS256")

    user = service.get_user(token)

    assert user.user_id == "USER002"
    assert user.user_name == "Minimal User"
    assert user.user_status == "ACTIVE"  # Default
    assert user.email == ""  # Default
    assert user.internal is True  # Default
    assert user.roles == {}  # Default


def test_build_headers_without_token(mock_settings):
    """Test _build_headers without token"""
    service = AtlasUserService(mock_settings)
    headers = service._build_headers()
    assert headers == {"Content-Type": "application/json"}


def test_build_headers_with_token(mock_settings):
    """Test _build_headers with token"""
    service = AtlasUserService(mock_settings)
    headers = service._build_headers("test_token")
    assert headers == {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"
    }


@pytest.mark.asyncio
async def test_get_all_users(mock_settings):
    """Test get_all fetches all users from API"""
    service = AtlasUserService(mock_settings)

    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "user_id": "USER001",
            "login_id": "user1",
            "user_name": "User One",
            "email": "user1@example.com",
            "phone": "1234567890",
            "roles": {},
            "creater_id": "system",
            "creater_name": "System",
            "updater_id": "system",
            "updater_name": "System"
        }
    ]
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        users = await service.get_all(token="test_token")

        assert len(users) == 1
        assert users[0].user_id == "USER001"


@pytest.mark.asyncio
async def test_get_by_id_found(mock_settings):
    """Test get_by_id returns user when found"""
    service = AtlasUserService(mock_settings)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "user_id": "USER001",
        "login_id": "user1",
        "user_name": "User One",
        "email": "user1@example.com",
        "phone": "1234567890",
        "roles": {},
        "creater_id": "system",
        "creater_name": "System",
        "updater_id": "system",
        "updater_name": "System"
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        user = await service.get_by_id("USER001")

        assert user is not None
        assert user.user_id == "USER001"


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_settings):
    """Test get_by_id returns None when not found"""
    service = AtlasUserService(mock_settings)

    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        user = await service.get_by_id("NONEXISTENT")

        assert user is None


@pytest.mark.asyncio
async def test_get_by_client_id(mock_settings):
    """Test get_by_client_id fetches users by client"""
    service = AtlasUserService(mock_settings)

    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "user_id": "USER001",
            "login_id": "user1",
            "user_name": "User One",
            "email": "user1@example.com",
            "phone": "1234567890",
            "client_id": "CLIENT001",
            "roles": {},
            "creater_id": "system",
            "creater_name": "System",
            "updater_id": "system",
            "updater_name": "System"
        }
    ]
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        users = await service.get_by_client_id("CLIENT001", token="test_token")

        assert len(users) == 1
        assert users[0].client_id == "CLIENT001"
