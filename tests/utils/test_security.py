"""Tests for security utilities"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from fastapi.security import SecurityScopes

from atlas_shared_app.utils.app_utils.security import (
    verify_user,
    verify_viewer,
    verify_editor,
    verify_admin,
    security_scheme,
)
from atlas_shared_app.entities.atlas_base_enums import AppEnum, UserAccess, UserRole
from atlas_shared_app.entities.atlas_user import AtlasUserRes


@pytest.fixture
def mock_request():
    """Create a mock request"""
    request = MagicMock()
    request.state = MagicMock()
    return request


@pytest.fixture
def mock_settings():
    """Create mock settings with identity settings"""
    from atlas_shared_app.settings.atlas_identity_settings import AtlasIdentitySettings
    settings = MagicMock()
    settings.app_id = AppEnum.ATLAS_APP_IDENTITY
    # Use actual AtlasIdentitySettings for the scopes dictionaries
    identity = AtlasIdentitySettings()
    settings.identity_settings = identity
    return settings


@pytest.fixture
def mock_credentials():
    """Create mock credentials"""
    credentials = MagicMock()
    credentials.credentials = "mock_token"
    return credentials


@pytest.fixture
def mock_user():
    """Create a mock user with editor role"""
    return AtlasUserRes(
        user_id="user-1",
        user_name="Test User",
        login_id="test_user",
        email="test@example.com",
        phone="1234567890",
        user_status="ACTIVE",
        internal=True,
        roles={AppEnum.ATLAS_APP_IDENTITY: UserRole.EDITOR},
        scopes={AppEnum.ATLAS_APP_IDENTITY: [UserAccess.VIEW, UserAccess.EDIT]},
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user"""
    return AtlasUserRes(
        user_id="admin-1",
        user_name="Admin User",
        login_id="admin_user",
        email="admin@example.com",
        phone="1234567890",
        user_status="ACTIVE",
        internal=True,
        roles={AppEnum.ATLAS_APP_IDENTITY: UserRole.ADMIN},
        scopes={AppEnum.ATLAS_APP_IDENTITY: [UserAccess.VIEW, UserAccess.EDIT, UserAccess.ADMIN]},
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )


@pytest.fixture
def inactive_user():
    """Create an inactive user"""
    return AtlasUserRes(
        user_id="inactive-1",
        user_name="Inactive User",
        login_id="inactive_user",
        email="inactive@example.com",
        phone="1234567890",
        user_status="INACTIVE",
        internal=True,
        roles={AppEnum.ATLAS_APP_IDENTITY: UserRole.VIEWER},
        scopes={AppEnum.ATLAS_APP_IDENTITY: [UserAccess.VIEW]},
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )


def test_security_scheme_exists():
    """Test that security_scheme is defined"""
    assert security_scheme is not None


@pytest.mark.asyncio
async def test_verify_user_success(mock_request, mock_settings, mock_credentials, mock_user):
    """Test verify_user returns user when valid"""
    mock_request.state.user = mock_user
    scopes = SecurityScopes(scopes=[UserAccess.VIEW])

    result = await verify_user(mock_request, mock_settings, mock_credentials, scopes)

    assert result == mock_user
    assert result.user_id == "user-1"


@pytest.mark.asyncio
async def test_verify_user_no_user(mock_request, mock_settings, mock_credentials):
    """Test verify_user raises 401 when no user in state"""
    mock_request.state.user = None
    scopes = SecurityScopes(scopes=[])

    with pytest.raises(HTTPException) as exc_info:
        await verify_user(mock_request, mock_settings, mock_credentials, scopes)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication required"


@pytest.mark.asyncio
async def test_verify_user_no_roles_for_app(mock_request, mock_settings, mock_credentials):
    """Test verify_user raises 401 when user has no roles for app"""
    user = AtlasUserRes(
        user_id="user-1",
        user_name="Test User",
        login_id="test_user",
        email="test@example.com",
        phone="1234567890",
        roles={AppEnum.ATLAS_APP_IDENTITY: ""},  # Empty role string
        scopes={},
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )
    mock_request.state.user = user
    scopes = SecurityScopes(scopes=[])

    with pytest.raises(HTTPException) as exc_info:
        await verify_user(mock_request, mock_settings, mock_credentials, scopes)

    assert exc_info.value.status_code == 403
    assert "does not have roles" in exc_info.value.detail


@pytest.mark.asyncio
async def test_verify_user_missing_scope(mock_request, mock_settings, mock_credentials):
    """Test verify_user raises 401 when user missing required scope"""
    user = AtlasUserRes(
        user_id="user-1",
        user_name="Test User",
        login_id="test_user",
        email="test@example.com",
        phone="1234567890",
        internal=True,
        roles={AppEnum.ATLAS_APP_IDENTITY: UserRole.VIEWER},
        scopes={AppEnum.ATLAS_APP_IDENTITY: [UserAccess.VIEW]},  # Viewer only has VIEW, not ADMIN
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )
    mock_request.state.user = user
    scopes = SecurityScopes(scopes=[UserAccess.ADMIN])

    with pytest.raises(HTTPException) as exc_info:
        await verify_user(mock_request, mock_settings, mock_credentials, scopes)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not enough permissions"


@pytest.mark.asyncio
async def test_verify_viewer_active_user(mock_user):
    """Test verify_viewer returns user when active"""
    result = await verify_viewer(mock_user)
    assert result == mock_user


@pytest.mark.asyncio
async def test_verify_viewer_inactive_user(inactive_user):
    """Test verify_viewer raises 400 for inactive user"""
    with pytest.raises(HTTPException) as exc_info:
        await verify_viewer(inactive_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"


@pytest.mark.asyncio
async def test_verify_editor_active_user(mock_user):
    """Test verify_editor returns user when active"""
    result = await verify_editor(mock_user)
    assert result == mock_user


@pytest.mark.asyncio
async def test_verify_editor_inactive_user(inactive_user):
    """Test verify_editor raises 400 for inactive user"""
    with pytest.raises(HTTPException) as exc_info:
        await verify_editor(inactive_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"


@pytest.mark.asyncio
async def test_verify_admin_active_user(mock_admin_user):
    """Test verify_admin returns user when active"""
    result = await verify_admin(mock_admin_user)
    assert result == mock_admin_user


@pytest.mark.asyncio
async def test_verify_admin_inactive_user(inactive_user):
    """Test verify_admin raises 400 for inactive user"""
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin(inactive_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"


@pytest.mark.asyncio
async def test_verify_user_external_user(mock_request, mock_settings, mock_credentials):
    """Test verify_user works for external users"""
    user = AtlasUserRes(
        user_id="ext-1",
        user_name="External User",
        login_id="ext_user",
        email="ext@example.com",
        phone="1234567890",
        internal=False,
        roles={AppEnum.ATLAS_APP_IDENTITY: UserRole.VIEWER},
        scopes={AppEnum.ATLAS_APP_IDENTITY: [UserAccess.VIEW]},
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )
    mock_request.state.user = user
    scopes = SecurityScopes(scopes=[UserAccess.VIEW])

    result = await verify_user(mock_request, mock_settings, mock_credentials, scopes)

    assert result == user
    assert result.internal is False
