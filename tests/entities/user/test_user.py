"""Tests for User entity"""

from atlas_shared_app.entities import AtlasUser, UserRole, AppEnum


def test_user_creation():
    """Test basic user creation"""
    user = AtlasUser(
        user_id="USER001",
        login_id="john.doe",
        user_name="John Doe",
        user_status="active",
        email="john@example.com",
        phone="+1234567890",
        client_id="CLIENT001",
        client_name="Test Client",
        creater_id="ADMIN001",
        creater_name="Admin User",
        updater_id="ADMIN001",
        updater_name="Admin User",
        internal=True,
        roles={AppEnum.ATLAS_APP_IDENTITY: UserRole.ADMIN, AppEnum.ATLAS_APP_NETWORK: UserRole.VIEWER},
    )
    assert user.user_id == "USER001"
    assert user.user_name == "John Doe"
    assert user.email == "john@example.com"
    assert user.phone == "+1234567890"
    assert user.internal is True
    assert user.roles == {AppEnum.ATLAS_APP_IDENTITY: UserRole.ADMIN, AppEnum.ATLAS_APP_NETWORK: UserRole.VIEWER}


def test_user_default_internal():
    """Test that internal defaults to True"""
    user = AtlasUser(
        user_id="USER002",
        login_id="jane.smith",
        user_name="Jane Smith",
        user_status="active",
        email="jane@example.com",
        phone="+0987654321",
        client_id="CLIENT001",
        client_name="Test Client",
        creater_id="ADMIN001",
        creater_name="Admin User",
        updater_id="ADMIN001",
        updater_name="Admin User",
        roles={AppEnum.ATLAS_APP_BILLING: UserRole.VIEWER},
    )
    assert user.internal is True
    assert user.roles == {AppEnum.ATLAS_APP_BILLING: UserRole.VIEWER}