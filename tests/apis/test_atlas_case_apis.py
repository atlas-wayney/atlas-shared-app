"""Tests for AtlasCaseAPIs"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_shared_app.apis.atlas_case_apis import router, register_case_apis
from atlas_shared_app.entities.atlas_case import AtlasCase, AtlasCaseStatus
from atlas_shared_app.entities.atlas_user import AtlasUserRes
from atlas_shared_app.database.atlas_asyncdb import get_engine
from atlas_shared_app.utils.app_utils.security import verify_viewer
from atlas_shared_app.settings.atlas_settings import get_case_settings


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
def mock_case_settings():
    settings = MagicMock()
    settings.case_types = {"support": MagicMock()}
    return settings


@pytest.fixture
def app(mock_user, mock_engine, mock_case_settings):
    app = FastAPI()
    app.include_router(router)

    # Override dependencies
    app.dependency_overrides[get_engine] = lambda: mock_engine
    app.dependency_overrides[verify_viewer] = lambda: mock_user
    app.dependency_overrides[get_case_settings] = lambda: mock_case_settings

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sample_case():
    return AtlasCase(
        case_id="case-123",
        case_type="support",
        title="Test Case",
        data={"field1": "value1"},
        case_status=AtlasCaseStatus.DRAFT,
        client_id="client-1",
        client_name="Test Client",
        entity_type="case",
        assigned_user_id="user-2",
        assigned_user_name="Assigned User",
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


@pytest.fixture
def sample_closed_case():
    return AtlasCase(
        case_id="case-closed",
        case_type="support",
        title="Closed Case",
        data={"field1": "value1"},
        case_status=AtlasCaseStatus.CLOSED,
        client_id="client-1",
        client_name="Test Client",
        entity_type="case",
        assigned_user_id="user-2",
        assigned_user_name="Assigned User",
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


@pytest.fixture
def sample_submitted_case():
    return AtlasCase(
        case_id="case-submitted",
        case_type="support",
        title="Submitted Case",
        data={"field1": "value1"},
        case_status=AtlasCaseStatus.SUBMITTED,
        client_id="client-1",
        client_name="Test Client",
        entity_type="case",
        assigned_user_id="user-2",
        assigned_user_name="Assigned User",
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


def test_register_case_apis():
    """Test that register_case_apis works correctly"""
    app = FastAPI()
    register_case_apis(app, "/api")
    # Check that router was registered
    assert len(app.routes) > 0


def test_router_has_routes():
    """Test that router has routes defined"""
    assert len(router.routes) > 0


@patch('atlas_shared_app.apis.atlas_case_apis.AtlasCaseService')
def test_get_case_found(mock_service_class, client, sample_case):
    """Test getting a case by ID - found"""
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = sample_case
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-cases/v1/case-123")

    assert response.status_code == 200
    assert response.json()["case_id"] == "case-123"


@patch('atlas_shared_app.apis.atlas_case_apis.AtlasCaseService')
def test_get_case_not_found(mock_service_class, client):
    """Test getting a case by ID - not found"""
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = None
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-cases/v1/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@patch('atlas_shared_app.apis.atlas_case_apis.AtlasCaseService')
def test_list_cases(mock_service_class, client, sample_case):
    """Test listing cases"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_case]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-cases/v1/")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_case_apis.AtlasCaseService')
def test_get_cases_by_client(mock_service_class, client, sample_case):
    """Test getting cases by client ID"""
    mock_service = AsyncMock()
    mock_service.get_by_client_id.return_value = [sample_case]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-cases/v1/client/client-1")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_case_apis.AtlasCaseService')
def test_get_cases_by_assigned_user(mock_service_class, client, sample_case):
    """Test getting cases by assigned user ID"""
    mock_service = AsyncMock()
    mock_service.get_by_assigned_user_id.return_value = [sample_case]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-cases/v1/user/user-2")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_case_apis.AtlasCaseService')
def test_get_cases_by_status(mock_service_class, client, sample_case):
    """Test getting cases by status"""
    mock_service = AsyncMock()
    mock_service.get_by_status.return_value = [sample_case]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-cases/v1/status/DRAFT")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_case_apis.AtlasCaseService')
def test_get_cases_by_status_invalid(mock_service_class, client):
    """Test getting cases by invalid status"""
    response = client.get("/atlas-cases/v1/status/INVALID_STATUS")

    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]


