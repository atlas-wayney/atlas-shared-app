"""Tests for base enums"""

from atlas_shared_app.entities import AppEnum, UserRole
from atlas_shared_app.entities.atlas_base_enums import SharedEnum


def test_shared_enum_values():
    """Test SharedEnum values"""
    assert SharedEnum.SYSTEM == "SYSTEM"
    assert SharedEnum.ALL == "ALL"
    assert SharedEnum.DEF == "DEFAULT"


def test_shared_enum_is_string():
    """Test that SharedEnum values are strings"""
    assert isinstance(SharedEnum.SYSTEM.value, str)
    assert isinstance(SharedEnum.ALL.value, str)
    assert isinstance(SharedEnum.DEF.value, str)


def test_user_role_values():
    """Test UserRole enum values"""
    assert UserRole.ADMIN == "ADMIN"
    assert UserRole.EDITOR == "EDITOR"
    assert UserRole.VIEWER == "VIEWER"


def test_user_role_membership():
    """Test UserRole enum membership"""
    assert hasattr(UserRole, "ADMIN")
    assert hasattr(UserRole, "EDITOR")
    assert hasattr(UserRole, "VIEWER")


def test_user_role_is_string():
    """Test that UserRole values are strings"""
    assert isinstance(UserRole.ADMIN.value, str)
    assert isinstance(UserRole.EDITOR.value, str)
    assert isinstance(UserRole.VIEWER.value, str)


def test_user_role_comparison():
    """Test UserRole string comparison"""
    assert UserRole.ADMIN.value == "ADMIN"
    assert str(UserRole.ADMIN.value) == "ADMIN"


def test_app_enum_values():
    """Test AppEnum values"""
    assert AppEnum.ATLAS_APP_IDENTITY == "ATLAS_APP_IDENTITY"
    assert AppEnum.ATLAS_APP_NETWORK == "ATLAS_APP_NETWORK"
    assert AppEnum.ATLAS_APP_BILLING == "ATLAS_APP_BILLING"


def test_app_enum_membership():
    """Test AppEnum membership"""
    assert hasattr(AppEnum, "ATLAS_APP_IDENTITY")
    assert hasattr(AppEnum, "ATLAS_APP_NETWORK")
    assert hasattr(AppEnum, "ATLAS_APP_BILLING")


def test_app_enum_is_string():
    """Test that AppEnum values are strings"""
    assert isinstance(AppEnum.ATLAS_APP_IDENTITY.value, str)
    assert isinstance(AppEnum.ATLAS_APP_NETWORK.value, str)


def test_app_enum_comparison():
    """Test AppEnum string comparison"""
    assert AppEnum.ATLAS_APP_IDENTITY.value == "ATLAS_APP_IDENTITY"
    assert str(AppEnum.ATLAS_APP_IDENTITY.value) == "ATLAS_APP_IDENTITY"


def test_app_enum_iteration():
    """Test that we can iterate over AppEnum"""
    app_values = list(AppEnum)
    assert len(app_values) >= 3
    assert AppEnum.ATLAS_APP_IDENTITY in app_values


def test_user_role_iteration():
    """Test that we can iterate over UserRole"""
    role_values = list(UserRole)
    assert len(role_values) == 3
    assert UserRole.ADMIN in role_values
    assert UserRole.EDITOR in role_values
    assert UserRole.VIEWER in role_values
