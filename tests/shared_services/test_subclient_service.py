"""Tests for AtlasSubclientService"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from atlas_shared_app.shared_services.atlas_subclient_service import AtlasSubclientService
from atlas_shared_app.settings.atlas_identity_settings import AtlasIdentitySettings
from atlas_shared_app.entities.atlas_subclient import AtlasSubclientRes


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
    return AtlasSubclientService(settings)


@pytest.fixture
def sample_subclient_data():
    """Sample subclient data with all required fields"""
    return {
        "subclient_id": "SUB001",
        "subclient_name": "Test Subclient",
        "subclient_status": "ACTIVE",
        "parent_subclient_id": "",
        "client_id": "CLIENT001",
        "client_name": "Test Client",
        "country": "US",
        "region": "NA",
        "tags": [],
        "create_time": "2024-01-01T00:00:00",
        "creater_id": "USER001",
        "creater_name": "Test User",
        "update_time": "2024-01-01T00:00:00",
        "updater_id": "USER001",
        "updater_name": "Test User",
    }


def test_service_init(settings):
    """Test service initialization"""
    service = AtlasSubclientService(settings)
    assert service.base_url == "https://api.example.com"
    assert service.timeout == 30.0


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


@pytest.mark.asyncio
async def test_get_all_success(service, sample_subclient_data):
    """Test getting all subclients successfully"""
    mock_response = MagicMock()
    mock_response.json.return_value = [sample_subclient_data]
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_all()

        assert len(result) == 1
        assert isinstance(result[0], AtlasSubclientRes)
        assert result[0].subclient_id == "SUB001"


@pytest.mark.asyncio
async def test_get_all_with_token(service):
    """Test getting all subclients with authentication token"""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        await service.get_all(token="test-token")

        call_args = mock_get.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_get_all_empty(service):
    """Test getting all subclients when none exist"""
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
async def test_get_by_id_found(service, sample_subclient_data):
    """Test getting a subclient by ID when found"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_subclient_data
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_by_id("SUB001")

        assert result is not None
        assert isinstance(result, AtlasSubclientRes)
        assert result.subclient_id == "SUB001"


@pytest.mark.asyncio
async def test_get_by_id_not_found(service):
    """Test getting a subclient by ID when not found"""
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_by_id("NONEXISTENT")
        assert result is None


@pytest.mark.asyncio
async def test_get_by_id_with_token(service, sample_subclient_data):
    """Test getting a subclient by ID with authentication token"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_subclient_data
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        await service.get_by_id("SUB001", token="test-token")

        call_args = mock_get.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_get_by_client_id_success(service, sample_subclient_data):
    """Test getting subclients by client ID"""
    sample_subclient_data_2 = sample_subclient_data.copy()
    sample_subclient_data_2["subclient_id"] = "SUB002"
    sample_subclient_data_2["subclient_name"] = "Test Subclient 2"

    mock_response = MagicMock()
    mock_response.json.return_value = [sample_subclient_data, sample_subclient_data_2]
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        result = await service.get_by_client_id("CLIENT001")

        assert len(result) == 2
        assert all(isinstance(r, AtlasSubclientRes) for r in result)
        # Verify the query parameter was passed
        call_args = mock_get.call_args
        assert call_args[1]["params"] == {"client_id": "CLIENT001"}


@pytest.mark.asyncio
async def test_get_by_client_id_with_token(service):
    """Test getting subclients by client ID with authentication token"""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get

        await service.get_by_client_id("CLIENT001", token="test-token")

        call_args = mock_get.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_get_by_client_id_empty(service):
    """Test getting subclients by client ID when none exist"""
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await service.get_by_client_id("CLIENT001")
        assert result == []


@pytest.mark.asyncio
async def test_get_by_id_http_error(service):
    """Test getting a subclient when HTTP error occurs"""
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
            await service.get_by_id("SUB001")


@pytest.mark.asyncio
async def test_get_all_404(service):
    """Test getting all subclients when endpoint returns 404"""
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
    """Test getting all subclients when HTTP error occurs"""
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
    """Test getting all subclients when request error occurs"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )

        with pytest.raises(httpx.RequestError):
            await service.get_all()


@pytest.mark.asyncio
async def test_get_by_id_request_error(service):
    """Test getting a subclient by ID when request error occurs"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )

        with pytest.raises(httpx.RequestError):
            await service.get_by_id("SUB001")


@pytest.mark.asyncio
async def test_get_by_client_id_http_error(service):
    """Test getting subclients by client ID when HTTP error occurs"""
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
            await service.get_by_client_id("CLIENT001")


@pytest.mark.asyncio
async def test_get_by_client_id_request_error(service):
    """Test getting subclients by client ID when request error occurs"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )

        with pytest.raises(httpx.RequestError):
            await service.get_by_client_id("CLIENT001")
