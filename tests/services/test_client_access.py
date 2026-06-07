"""Tests for client access utilities"""

import pytest
from fastapi import HTTPException

from atlas_shared_app.services.client_access import (
    is_external_user,
    get_user_client_id,
    validate_client_access,
    get_client_filter_for_user,
)
from atlas_shared_app.entities.atlas_user import AtlasUserRes


@pytest.fixture
def internal_user():
    """Create an internal user"""
    return AtlasUserRes(
        user_id="internal-1",
        user_name="Internal User",
        login_id="internal_user",
        email="internal@example.com",
        phone="1234567890",
        internal=True,
        roles={},
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )


@pytest.fixture
def external_user():
    """Create an external user with client"""
    return AtlasUserRes(
        user_id="external-1",
        user_name="External User",
        login_id="external_user",
        email="external@example.com",
        phone="1234567890",
        internal=False,
        client_id="client-1",
        client_name="Test Client",
        roles={},
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )


def test_is_external_user_internal(internal_user):
    """Test is_external_user returns False for internal user"""
    assert is_external_user(internal_user) is False


def test_is_external_user_external(external_user):
    """Test is_external_user returns True for external user"""
    assert is_external_user(external_user) is True


def test_get_user_client_id_internal(internal_user):
    """Test get_user_client_id returns None for internal user"""
    result = get_user_client_id(internal_user)
    assert result is None


def test_get_user_client_id_external(external_user):
    """Test get_user_client_id returns client_id for external user"""
    result = get_user_client_id(external_user)
    assert result == "client-1"


def test_validate_client_access_internal_user(internal_user):
    """Test internal users always have access"""
    # Should not raise for any client_id
    validate_client_access(internal_user, "client-1")
    validate_client_access(internal_user, "client-2")
    validate_client_access(internal_user, None)


def test_validate_client_access_external_same_client(external_user):
    """Test external users can access their own client's data"""
    # Should not raise
    validate_client_access(external_user, "client-1")


def test_validate_client_access_external_different_client(external_user):
    """Test external users cannot access other client's data"""
    with pytest.raises(HTTPException) as exc_info:
        validate_client_access(external_user, "client-2")

    assert exc_info.value.status_code == 403
    assert "do not have permission" in exc_info.value.detail


def test_validate_client_access_external_no_client_resource(external_user):
    """Test external users cannot access resources without client association"""
    with pytest.raises(HTTPException) as exc_info:
        validate_client_access(external_user, None)

    assert exc_info.value.status_code == 403
    assert "without a client association" in exc_info.value.detail


def test_get_client_filter_for_user_internal(internal_user):
    """Test get_client_filter_for_user returns None for internal user"""
    result = get_client_filter_for_user(internal_user)
    assert result is None


def test_get_client_filter_for_user_external(external_user):
    """Test get_client_filter_for_user returns client_id for external user"""
    result = get_client_filter_for_user(external_user)
    assert result == "client-1"
