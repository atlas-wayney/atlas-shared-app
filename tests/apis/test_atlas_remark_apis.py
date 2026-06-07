"""Tests for AtlasRemarkAPIs"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_shared_app.apis.atlas_remark_apis import router, register_remark_apis
from atlas_shared_app.entities.atlas_remark import AtlasRemark
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
def sample_remark():
    return AtlasRemark(
        remark_id="remark-123",
        entity_type="case",
        entity_id="case-456",
        remark="Test remark content",
        internal_only=False,
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


def test_register_remark_apis():
    """Test that register_remark_apis works correctly"""
    app = FastAPI()
    register_remark_apis(app, "/api")
    # Check that router was registered
    assert len(app.routes) > 0


@patch('atlas_shared_app.apis.atlas_remark_apis.AtlasRemarkService')
def test_create_remark(mock_service_class, client, sample_remark):
    """Test creating a remark"""
    mock_service = AsyncMock()
    mock_service.create.return_value = sample_remark
    mock_service_class.return_value = mock_service

    response = client.post(
        "/atlas-remarks/v1/",
        json={
            "entity_type": "case",
            "entity_id": "case-456",
            "remark": "Test remark content",
            "internal_only": False
        }
    )

    assert response.status_code == 201
    assert response.json()["remark_id"] == "remark-123"


@patch('atlas_shared_app.apis.atlas_remark_apis.AtlasRemarkService')
def test_get_remark_found(mock_service_class, client, sample_remark):
    """Test getting a remark by ID when found"""
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = sample_remark
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-remarks/v1/remark-123")

    assert response.status_code == 200
    assert response.json()["remark_id"] == "remark-123"


@patch('atlas_shared_app.apis.atlas_remark_apis.AtlasRemarkService')
def test_get_remark_not_found(mock_service_class, client):
    """Test getting a remark by ID when not found"""
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = None
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-remarks/v1/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@patch('atlas_shared_app.apis.atlas_remark_apis.AtlasRemarkService')
def test_list_remarks(mock_service_class, client, sample_remark):
    """Test listing all remarks"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_remark]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-remarks/v1/")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_remark_apis.AtlasRemarkService')
def test_list_remarks_with_pagination(mock_service_class, client, sample_remark):
    """Test listing remarks with pagination parameters"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_remark]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-remarks/v1/?skip=10&limit=50")

    assert response.status_code == 200


@patch('atlas_shared_app.apis.atlas_remark_apis.AtlasRemarkService')
def test_delete_remark_success(mock_service_class, client):
    """Test deleting a remark successfully"""
    mock_service = AsyncMock()
    mock_service.delete.return_value = True
    mock_service_class.return_value = mock_service

    response = client.delete("/atlas-remarks/v1/remark-123")

    assert response.status_code == 204


@patch('atlas_shared_app.apis.atlas_remark_apis.AtlasRemarkService')
def test_delete_remark_not_found(mock_service_class, client):
    """Test deleting a remark when not found"""
    mock_service = AsyncMock()
    mock_service.delete.return_value = False
    mock_service_class.return_value = mock_service

    response = client.delete("/atlas-remarks/v1/nonexistent")

    assert response.status_code == 404


@patch('atlas_shared_app.apis.atlas_remark_apis.AtlasRemarkService')
def test_get_remarks_by_entity(mock_service_class, client, sample_remark):
    """Test getting remarks by entity ID"""
    mock_service = AsyncMock()
    mock_service.get_by_entity_id.return_value = [sample_remark]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-remarks/v1/entity/case-456")

    assert response.status_code == 200
    assert len(response.json()) == 1
