"""Tests for AtlasDocumentAPIs"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_shared_app.apis.atlas_document_apis import router, register_document_apis
from atlas_shared_app.entities.atlas_document import AtlasDocument
from atlas_shared_app.entities.atlas_user import AtlasUserRes
from atlas_shared_app.database.atlas_asyncdb import get_engine
from atlas_shared_app.utils.app_utils.security import verify_viewer, verify_editor
from atlas_shared_app.settings.atlas_settings import get_document_settings


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
def mock_document_settings():
    settings = MagicMock()
    settings.bucket = "test-bucket"
    return settings


@pytest.fixture
def app(mock_user, mock_engine, mock_document_settings):
    app = FastAPI()
    app.include_router(router)

    # Override dependencies
    app.dependency_overrides[get_engine] = lambda: mock_engine
    app.dependency_overrides[verify_viewer] = lambda: mock_user
    app.dependency_overrides[verify_editor] = lambda: mock_user
    app.dependency_overrides[get_document_settings] = lambda: mock_document_settings

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sample_document():
    return AtlasDocument(
        document_id="doc-123",
        document_name="test.pdf",
        entity_type="case",
        entity_id="case-456",
        bucket="test-bucket",
        fullpath="/path/to/test.pdf",
        internal_only=False,
        deleted=False,
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


def test_register_document_apis():
    """Test that register_document_apis works correctly"""
    app = FastAPI()
    register_document_apis(app, "/api")
    # Check that router was registered
    assert len(app.routes) > 0


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_create_document(mock_service_class, client, sample_document):
    """Test creating a document"""
    mock_service = AsyncMock()
    mock_service.create.return_value = sample_document
    mock_service_class.return_value = mock_service

    response = client.post(
        "/atlas-documents/v1/",
        json={
            "document_name": "test.pdf",
            "entity_type": "case",
            "entity_id": "case-456"
        }
    )

    assert response.status_code == 201
    assert response.json()["document_id"] == "doc-123"


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_get_document_found(mock_service_class, client, sample_document):
    """Test getting a document by ID when found"""
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = sample_document
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-documents/v1/doc-123")

    assert response.status_code == 200
    assert response.json()["document_id"] == "doc-123"


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_get_document_not_found(mock_service_class, client):
    """Test getting a document by ID when not found"""
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = None
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-documents/v1/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_list_documents(mock_service_class, client, sample_document):
    """Test listing all documents"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_document]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-documents/v1/")

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_list_documents_with_pagination(mock_service_class, client, sample_document):
    """Test listing documents with pagination parameters"""
    mock_service = AsyncMock()
    mock_service.get_all.return_value = [sample_document]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-documents/v1/?skip=10&limit=50")

    assert response.status_code == 200


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_update_document_success(mock_service_class, client, sample_document):
    """Test updating a document successfully"""
    mock_service = AsyncMock()
    mock_service.update.return_value = sample_document
    mock_service_class.return_value = mock_service

    response = client.put(
        "/atlas-documents/v1/doc-123",
        json={
            "document_name": "updated.pdf",
            "entity_type": "case",
            "entity_id": "case-456"
        }
    )

    assert response.status_code == 200


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_update_document_not_found(mock_service_class, client):
    """Test updating a document when not found"""
    mock_service = AsyncMock()
    mock_service.update.return_value = None
    mock_service_class.return_value = mock_service

    response = client.put(
        "/atlas-documents/v1/nonexistent",
        json={
            "document_name": "updated.pdf",
            "entity_type": "case",
            "entity_id": "case-456"
        }
    )

    assert response.status_code == 404


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_delete_document_success(mock_service_class, client):
    """Test deleting a document successfully"""
    mock_service = AsyncMock()
    mock_service.delete.return_value = True
    mock_service_class.return_value = mock_service

    response = client.delete("/atlas-documents/v1/doc-123")

    assert response.status_code == 204


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_delete_document_not_found(mock_service_class, client):
    """Test deleting a document when not found"""
    mock_service = AsyncMock()
    mock_service.delete.return_value = False
    mock_service_class.return_value = mock_service

    response = client.delete("/atlas-documents/v1/nonexistent")

    assert response.status_code == 404


@patch('atlas_shared_app.apis.atlas_document_apis.AtlasDocumentService')
def test_get_documents_by_entity(mock_service_class, client, sample_document):
    """Test getting documents by entity ID"""
    mock_service = AsyncMock()
    mock_service.get_by_entity_id.return_value = [sample_document]
    mock_service_class.return_value = mock_service

    response = client.get("/atlas-documents/v1/entity/case-456")

    assert response.status_code == 200
    assert len(response.json()) == 1
