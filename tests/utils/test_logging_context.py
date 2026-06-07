"""Tests for logging context utilities"""

import pytest
from atlas_shared_app.utils.logging_utils.logging_context import (
    set_request_context,
    clear_request_context,
    get_request_id,
    get_user_id,
    get_client_id,
    context_filter,
)


def test_set_and_get_request_context():
    """Test setting and getting request context"""
    set_request_context(
        request_id="req-123",
        user_id="user-456",
        client_id="client-789"
    )

    assert get_request_id() == "req-123"
    assert get_user_id() == "user-456"
    assert get_client_id() == "client-789"

    clear_request_context()


def test_get_request_id_default():
    """Test get_request_id returns default when not set"""
    clear_request_context()
    assert get_request_id() == "-"


def test_get_user_id_default():
    """Test get_user_id returns None when not set"""
    clear_request_context()
    assert get_user_id() is None


def test_get_client_id_default():
    """Test get_client_id returns None when not set"""
    clear_request_context()
    assert get_client_id() is None


def test_set_request_context_generates_request_id():
    """Test that request_id is auto-generated if not provided"""
    set_request_context(user_id="user-123")

    request_id = get_request_id()
    assert request_id != "-"
    assert len(request_id) > 0

    clear_request_context()


def test_clear_request_context():
    """Test clearing request context"""
    set_request_context(
        request_id="req-123",
        user_id="user-456",
        client_id="client-789"
    )

    clear_request_context()

    assert get_request_id() == "-"
    assert get_user_id() is None
    assert get_client_id() is None


def test_context_filter_with_context():
    """Test context_filter adds context to log record"""
    set_request_context(
        request_id="req-123",
        user_id="user-456",
        client_id="client-789"
    )

    record = {"extra": {}}
    result = context_filter(record)

    assert result is True
    assert record["extra"]["request_id"] == "req-123"
    assert record["extra"]["user_id"] == "user-456"
    assert record["extra"]["client_id"] == "client-789"

    clear_request_context()


def test_context_filter_without_context():
    """Test context_filter uses defaults when context not set"""
    clear_request_context()

    record = {"extra": {}}
    result = context_filter(record)

    assert result is True
    assert record["extra"]["request_id"] == "-"
    assert record["extra"]["user_id"] == "-"
    assert record["extra"]["client_id"] == "-"
