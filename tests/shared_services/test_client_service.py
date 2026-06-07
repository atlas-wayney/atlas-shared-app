"""Tests for AtlasClientService"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from atlas_shared_app.shared_services.atlas_client_service import AtlasClientService
from atlas_shared_app.settings.atlas_identity_settings import AtlasIdentitySettings
from atlas_shared_app.entities.atlas_client import AtlasClientRes


@pytest.fixture
def settings():
    """Create test settings"""
    return AtlasIdentitySettings(
        base_url="https://api.example.com/",
        timeout=30.0,
    )


@pytest.fixture
def service(settings):
    """Create service instance"""
    return AtlasClientService(settings)


def test_service_init(settings):
    """Test service initialization"""
    service = AtlasClientService(settings)
    assert service.base_url == "https://api.example.com"
    assert service.timeout == 30.0


def test_service_init_strips_trailing_slash():
    """Test that trailing slash is stripped from base_url"""
    settings = AtlasIdentitySettings(
        base_url="https://api.example.com/",
        timeout=30.0,
    )
    service = AtlasClientService(settings)
    assert service.base_url == "https://api.example.com"


def test_build_headers_without_token(service):
    """Test building headers without token"""
    headers = service._build_headers()
    assert headers == {"Content-Type": "application/json"}


def test_build_headers_with_token(service):
    """Test building headers with token"""
    headers = service._build_headers("test-token")
    assert headers == {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token",
    }


@pytest.fixture
def sample_client_data():
    """Sample client data with all required fields"""
    return {
        "client_id": "CLIENT001",
        "client_name": "Test Client",
        "client_status": "ACTIVE",
        "supported_email_domains": ["test.com"],
        "allowed_apps": [],
        "tags": [],
        "terms_acceptances": {},
        "create_time": "2024-01-01T00:00:00",
        "creater_id": "USER001",
        "creater_name": "Test User",
        "update_time": "2024-01-01T00:00:00",
        "updater_id": "USER001",
        "updater_name": "Test User",
    }


@pytest.mark.asyncio
async def test_get_all_success(service, sample_client_data):
    """Test getting all clients successfully"""
    mock_response = MagicMock()
    mock_response.json.return_value = [sample_client_data]
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_all()

        assert len(result) == 1
        assert isinstance(result[0], AtlasClientRes)
        assert result[0].client_id == "CLIENT001"


@pytest.mark.asyncio
async def test_get_all_with_token(service):
    """Test getting all clients with authentication token"""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        await service.get_all(token="test-token")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_get_all_empty(service):
    """Test getting all clients when none exist"""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_all()
        assert result == []


@pytest.mark.asyncio
async def test_get_by_id_found(service, sample_client_data):
    """Test getting a client by ID when found"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_client_data
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_by_id("CLIENT001")

        assert result is not None
        assert isinstance(result, AtlasClientRes)
        assert result.client_id == "CLIENT001"


@pytest.mark.asyncio
async def test_get_by_id_not_found(service):
    """Test getting a client by ID when not found"""
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_by_id("NONEXISTENT")
        assert result is None


@pytest.mark.asyncio
async def test_get_by_id_with_token(service, sample_client_data):
    """Test getting a client by ID with authentication token"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_client_data
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        await service.get_by_id("CLIENT001", token="test-token")

        call_args = mock_get.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_get_by_id_http_error(service):
    """Test getting a client when HTTP error occurs"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Internal Server Error",
        request=MagicMock(),
        response=mock_response,
    )

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        with pytest.raises(httpx.HTTPStatusError):
            await service.get_by_id("CLIENT001")


@pytest.mark.asyncio
async def test_get_all_404(service):
    """Test getting all clients when endpoint returns 404"""
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_all()
        assert result == []


@pytest.mark.asyncio
async def test_get_all_http_error(service):
    """Test getting all clients when HTTP error occurs"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Internal Server Error",
        request=MagicMock(),
        response=mock_response,
    )

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        with pytest.raises(httpx.HTTPStatusError):
            await service.get_all()


@pytest.mark.asyncio
async def test_get_all_request_error(service):
    """Test getting all clients when request error occurs"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )

        with pytest.raises(httpx.RequestError):
            await service.get_all()


@pytest.mark.asyncio
async def test_get_by_id_request_error(service):
    """Test getting a client by ID when request error occurs"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )

        with pytest.raises(httpx.RequestError):
            await service.get_by_id("CLIENT001")
