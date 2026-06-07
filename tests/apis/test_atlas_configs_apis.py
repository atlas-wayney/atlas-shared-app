"""Tests for AtlasConfigsAPIs"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_shared_app.apis.atlas_configs_apis import router, register_configs_apis
from atlas_shared_app.entities.atlas_configs import AtlasConfigs
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
def sample_config():
    return AtlasConfigs(
        config_type="case",
        entity_type="case",
        field_name="status",
        options={"DRAFT": "Draft", "SUBMITTED": "Submitted", "CLOSED": "Closed"},
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


def test_register_configs_apis():
    """Test that register_configs_apis works correctly"""
    app = FastAPI()
    register_configs_apis(app, "/api")
    # Check that router was registered
    assert len(app.routes) > 0


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_create_config(mock_service_class, client, sample_config):
    """Test creating a config"""
    mock_service = AsyncMock()
    mock_service.create.return_value = sample_config
    mock_service_class.return_value = mock_service

    response = client.post(
        "/atlas-configs/v1/",
        json={
            "config_type": "case",
            "entity_type": "case",
            "field_name": "status",
            "options": {"DRAFT": "Draft", "SUBMITTED": "Submitted", "CLOSED": "Closed"}
        }
    )

    assert response.status_code == 201
    assert response.json()["field_name"] == "status"


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_get_config_found(mock_service_class, client, sample_config):
    """Test getting a config by type and field_name when found"""
    mock_service = AsyncMock()
    mock_service.get.return_value = {"status": sample_config}
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-configs/v1/case/status")

    assert response.status_code == 200
    assert response.json()["field_name"] == "status"


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_get_config_not_found(mock_service_class, client):
    """Test getting a config when not found"""
    mock_service = AsyncMock()
    mock_service.get.return_value = {}
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-configs/v1/case/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_get_configs_by_type(mock_service_class, client, sample_config):
    """Test getting configs by type"""
    mock_service = AsyncMock()
    mock_service.get_by_entity_type.return_value = [sample_config]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-configs/v1/case")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_list_configs(mock_service_class, client, sample_config):
    """Test listing all configs"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_config]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-configs/v1/")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_list_configs_with_pagination(mock_service_class, client, sample_config):
    """Test listing configs with pagination parameters"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_config]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-configs/v1/?skip=10&limit=50")

    assert response.status_code == 200


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_update_config_success(mock_service_class, client, sample_config):
    """Test updating a config successfully"""
    mock_service = AsyncMock()
    mock_service.update.return_value = sample_config
    mock_service_class.return_value = mock_service

    response = client.put(
        "/atlas-configs/v1/case/status",
        json={
            "config_type": "case",
            "entity_type": "case",
            "field_name": "status",
            "options": {"NEW": "New", "OPTIONS": "Options"}
        }
    )

    assert response.status_code == 200


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_update_config_not_found(mock_service_class, client):
    """Test updating a config when not found"""
    mock_service = AsyncMock()
    mock_service.update.return_value = None
    mock_service_class.return_value = mock_service

    response = client.put(
        "/atlas-configs/v1/case/nonexistent",
        json={
            "config_type": "case",
            "entity_type": "case",
            "field_name": "nonexistent",
            "options": {"NEW": "New"}
        }
    )

    assert response.status_code == 404


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_delete_config_success(mock_service_class, client):
    """Test deleting a config successfully"""
    mock_service = AsyncMock()
    mock_service.delete.return_value = True
    mock_service_class.return_value = mock_service

    response = client.delete("/atlas-configs/v1/case/status")

    assert response.status_code == 204


@patch('atlas_shared_app.apis.atlas_configs_apis.AtlasConfigsService')
def test_delete_config_not_found(mock_service_class, client):
    """Test deleting a config when not found"""
    mock_service = AsyncMock()
    mock_service.delete.return_value = False
    mock_service_class.return_value = mock_service

    response = client.delete("/atlas-configs/v1/case/nonexistent")

    assert response.status_code == 404
