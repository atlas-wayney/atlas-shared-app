"""Tests for AtlasHistoryAPIs"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_shared_app.apis.atlas_history_apis import router, register_history_apis
from atlas_shared_app.entities.atlas_history import AtlasHistory
from atlas_shared_app.entities.atlas_user import AtlasUserRes
from atlas_shared_app.database.atlas_asyncdb import get_engine
from atlas_shared_app.utils.app_utils.security import verify_viewer, verify_editor


@pytest.fixture
def mock_user():
    return AtlasUserRes(
        user_id="user-1",
        user_name="Test User",
        login_id="test_user",
        email="test@example.com",
        phone="1234567890",
        roles={},
        creater_id="system",
        creater_name="System",
        updater_id="system",
        updater_name="System"
    )


@pytest.fixture
def mock_engine():
    return AsyncMock()


@pytest.fixture
def app(mock_user, mock_engine):
    app = FastAPI()
    app.include_router(router)

    # Override dependencies
    app.dependency_overrides[get_engine] = lambda: mock_engine
    app.dependency_overrides[verify_viewer] = lambda: mock_user
    app.dependency_overrides[verify_editor] = lambda: mock_user

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sample_history():
    return AtlasHistory(
        history_id="history-123",
        entity_type="case",
        entity_id="case-456",
        action="CREATE",
        description="Test history entry",
        internal_only=False,
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


def test_register_history_apis():
    """Test that register_history_apis works correctly"""
    app = FastAPI()
    register_history_apis(app, "/api")
    # Check that router was registered
    assert len(app.routes) > 0


@patch('atlas_shared_app.apis.atlas_history_apis.AtlasHistoryService')
def test_create_history(mock_service_class, client, sample_history):
    """Test creating a history entry"""
    mock_service = AsyncMock()
    mock_service.create.return_value = sample_history
    mock_service_class.return_value = mock_service

    response = client.post(
        "/atlas-histories/v1/",
        json={
            "entity_type": "case",
            "entity_id": "case-456",
            "action": "CREATE",
            "description": "Test history entry",
            "internal_only": False
        }
    )

    assert response.status_code == 201
    assert response.json()["history_id"] == "history-123"


@patch('atlas_shared_app.apis.atlas_history_apis.AtlasHistoryService')
def test_get_history_found(mock_service_class, client, sample_history):
    """Test getting a history entry by ID when found"""
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = sample_history
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-histories/v1/history-123")

    assert response.status_code == 200
    assert response.json()["history_id"] == "history-123"


@patch('atlas_shared_app.apis.atlas_history_apis.AtlasHistoryService')
def test_get_history_not_found(mock_service_class, client):
    """Test getting a history entry by ID when not found"""
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = None
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-histories/v1/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@patch('atlas_shared_app.apis.atlas_history_apis.AtlasHistoryService')
def test_list_histories(mock_service_class, client, sample_history):
    """Test listing all history entries"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_history]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-histories/v1/")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_history_apis.AtlasHistoryService')
def test_list_histories_with_pagination(mock_service_class, client, sample_history):
    """Test listing history entries with pagination parameters"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_history]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-histories/v1/?skip=10&limit=50")

    assert response.status_code == 200


@patch('atlas_shared_app.apis.atlas_history_apis.AtlasHistoryService')
def test_get_histories_by_entity(mock_service_class, client, sample_history):
    """Test getting history entries by entity ID"""
    mock_service = AsyncMock()
    mock_service.get_by_entity_id.return_value = [sample_history]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-histories/v1/entity/case-456")

    assert response.status_code == 200
    assert len(response.json()) == 1
