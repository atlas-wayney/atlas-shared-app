"""Tests for AtlasSettings and getter functions"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI

from atlas_shared_app.settings.atlas_settings import (
    AtlasSettings,
    get_identity_settings,
    get_case_settings,
    get_document_settings,
)
from atlas_shared_app.settings.atlas_db_settings import AtlasDbSettings
from atlas_shared_app.settings.atlas_identity_settings import AtlasIdentitySettings
from atlas_shared_app.settings.atlas_case_settings import AtlasCaseSettings
from atlas_shared_app.settings.atlas_document_settings import AtlasDocumentSettings
from atlas_shared_app.settings.atlas_workflow_settings import AtlasWorkflowSettings


def test_atlas_settings_default_values():
    """Test AtlasSettings default values"""
    with patch.dict('os.environ', {}, clear=True):
        settings = AtlasSettings()
        assert settings.is_local is False
        assert settings.app_id == ""
        assert isinstance(settings.db_settings, AtlasDbSettings)
        assert isinstance(settings.identity_settings, AtlasIdentitySettings)
        assert isinstance(settings.case_settings, AtlasCaseSettings)
        assert isinstance(settings.document_settings, AtlasDocumentSettings)
        assert isinstance(settings.workflow_settings, AtlasWorkflowSettings)


def test_atlas_settings_custom_values():
    """Test AtlasSettings with custom values"""
    settings = AtlasSettings(
        is_local=True,
        app_id="custom_app",
    )
    assert settings.is_local is True
    assert settings.app_id == "custom_app"


def test_atlas_db_settings_default():
    """Test AtlasDbSettings default values"""
    with patch.dict('os.environ', {}, clear=True):
        settings = AtlasDbSettings()
        assert settings.host_with_port == ""
        assert settings.name == ""
        assert settings.user == ""
        assert settings.secret_password.get_secret_value() == ""


def test_atlas_db_settings_custom():
    """Test AtlasDbSettings with custom values"""
    settings = AtlasDbSettings(
        host_with_port="localhost:5432",
        name="mydb",
        user="admin",
        secret_password="secret"
    )
    assert settings.host_with_port == "localhost:5432"
    assert settings.name == "mydb"
    assert settings.user == "admin"
    assert settings.secret_password.get_secret_value() == "secret"


def test_atlas_identity_settings_default():
    """Test AtlasIdentitySettings default values"""
    settings = AtlasIdentitySettings()
    assert settings.base_url == ""
    assert settings.timeout == 30.0
    assert settings.jwt_algorithm == "RS256"
    assert "BEGIN RSA PRIVATE KEY" in settings.secret_jwt_private_key.get_secret_value()
    assert "BEGIN PUBLIC KEY" in settings.secret_jwt_public_key.get_secret_value()


def test_atlas_case_settings_default():
    """Test AtlasCaseSettings default values"""
    settings = AtlasCaseSettings()
    assert settings.case_types == {}


def test_atlas_document_settings_default():
    """Test AtlasDocumentSettings default values"""
    settings = AtlasDocumentSettings()
    assert settings.bucket == ""
    assert settings.project_id == ""


def test_get_identity_settings_success():
    """Test get_identity_settings with valid settings"""
    mock_request = MagicMock()
    mock_identity_settings = AtlasIdentitySettings()
    mock_atlas_settings = AtlasSettings(identity_settings=mock_identity_settings)
    mock_request.app.state.atlas_settings = mock_atlas_settings

    result = get_identity_settings(mock_request)
    assert result == mock_identity_settings


def test_get_identity_settings_no_atlas_settings():
    """Test get_identity_settings when atlas_settings is None"""
    mock_request = MagicMock()
    mock_request.app.state.atlas_settings = None

    with pytest.raises(ValueError) as exc_info:
        get_identity_settings(mock_request)
    assert "AtlasSettings is not initialized" in str(exc_info.value)


def test_get_identity_settings_no_identity_settings():
    """Test get_identity_settings when identity_settings is None"""
    mock_request = MagicMock()
    mock_atlas_settings = MagicMock()
    mock_atlas_settings.identity_settings = None
    mock_request.app.state.atlas_settings = mock_atlas_settings

    with pytest.raises(ValueError) as exc_info:
        get_identity_settings(mock_request)
    assert "AtlasIdentitySettings is not initialized" in str(exc_info.value)


def test_get_case_settings_success():
    """Test get_case_settings with valid settings"""
    mock_request = MagicMock()
    mock_case_settings = AtlasCaseSettings()
    mock_atlas_settings = AtlasSettings(case_settings=mock_case_settings)
    mock_request.app.state.atlas_settings = mock_atlas_settings

    result = get_case_settings(mock_request)
    assert result == mock_case_settings


def test_get_case_settings_no_atlas_settings():
    """Test get_case_settings when atlas_settings is None"""
    mock_request = MagicMock()
    mock_request.app.state.atlas_settings = None

    with pytest.raises(ValueError) as exc_info:
        get_case_settings(mock_request)
    assert "AtlasSettings is not initialized" in str(exc_info.value)


def test_get_case_settings_no_case_settings():
    """Test get_case_settings when case_settings is None"""
    mock_request = MagicMock()
    mock_atlas_settings = MagicMock()
    mock_atlas_settings.case_settings = None
    mock_request.app.state.atlas_settings = mock_atlas_settings

    with pytest.raises(ValueError) as exc_info:
        get_case_settings(mock_request)
    assert "AtlasCaseSettings is not initialized" in str(exc_info.value)


def test_get_document_settings_success():
    """Test get_document_settings with valid settings"""
    mock_request = MagicMock()
    mock_doc_settings = AtlasDocumentSettings()
    mock_atlas_settings = AtlasSettings(document_settings=mock_doc_settings)
    mock_request.app.state.atlas_settings = mock_atlas_settings

    result = get_document_settings(mock_request)
    assert result == mock_doc_settings


def test_get_document_settings_no_atlas_settings():
    """Test get_document_settings when atlas_settings is None"""
    mock_request = MagicMock()
    mock_request.app.state.atlas_settings = None

    with pytest.raises(ValueError) as exc_info:
        get_document_settings(mock_request)
    assert "AtlasSettings is not initialized" in str(exc_info.value)


def test_get_document_settings_no_document_settings():
    """Test get_document_settings when document_settings is None"""
    mock_request = MagicMock()
    mock_atlas_settings = MagicMock()
    mock_atlas_settings.document_settings = None
    mock_request.app.state.atlas_settings = mock_atlas_settings

    with pytest.raises(ValueError) as exc_info:
        get_document_settings(mock_request)
    assert "AtlasDocumentSettings is not initialized" in str(exc_info.value)


def test_atlas_workflow_settings_default():
    """Test AtlasWorkflowSettings default values"""
    with patch.dict('os.environ', {}, clear=True):
        settings = AtlasWorkflowSettings()
        assert settings.secret_temporal_api_key.get_secret_value() == ""
        assert settings.temporal_namespace == ""
        assert settings.temporal_address == ""


def test_atlas_workflow_settings_custom():
    """Test AtlasWorkflowSettings with custom values"""
    settings = AtlasWorkflowSettings(
        secret_temporal_api_key="my-api-key",
        temporal_namespace="my-namespace",
        temporal_address="localhost:7233"
    )
    assert settings.secret_temporal_api_key.get_secret_value() == "my-api-key"
    assert settings.temporal_namespace == "my-namespace"
    assert settings.temporal_address == "localhost:7233"

