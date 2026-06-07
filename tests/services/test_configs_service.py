"""Tests for Configs service - unit tests without database"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from atlas_shared_app.entities import AtlasConfigsBase, UserRole
from atlas_shared_app.entities.atlas_user import AtlasUserBase
from atlas_shared_app.entities.atlas_configs import AtlasConfigs
from atlas_shared_app.services.atlas_configs_service import AtlasConfigsService


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return AtlasUserBase(
        user_id="USER001",
        login_id="testuser",
        user_name="Test User",
        user_status="active",
        email="test@example.com",
        phone="+1234567890",
        internal=True,
        roles=[UserRole.ADMIN],
    )


@pytest.fixture
def sample_config():
    """Create a sample config for testing"""
    return AtlasConfigsBase(
        entity_type="case",
        field_name="priority",
        options={"low": "Low", "medium": "Medium", "high": "High"},
    )


@pytest.fixture
def mock_engine():
    """Create a mock engine for testing"""
    return MagicMock()


@pytest.fixture
def mock_user_res():
    """Create a mock user response for testing"""
    from atlas_shared_app.entities.atlas_user import AtlasUserRes
    return AtlasUserRes(
        user_id="USER001",
        login_id="testuser",
        user_name="Test User",
        user_status="active",
        email="test@example.com",
        phone="+1234567890",
        internal=True,
        roles={},
        creater_id="USER001",
        creater_name="Test User",
        updater_id="USER001",
        updater_name="Test User"
    )


def test_configs_service_init(mock_engine):
    """Test ConfigsService initialization"""
    with patch('atlas_shared_app.services.atlas_configs_service.AtlasConfigsRepository'):
        service = AtlasConfigsService(mock_engine)
        assert service.repository is not None


@pytest.mark.asyncio
async def test_configs_service_get(mock_engine, mock_user_res):
    """Test getting configs by config type"""
    with patch('atlas_shared_app.services.atlas_configs_service.AtlasConfigsRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get = AsyncMock(return_value={
            "priority": AtlasConfigs(
                entity_type="case",
                field_name="priority",
                options={"low": "Low", "medium": "Medium", "high": "High"},
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            )
        })

        service = AtlasConfigsService(mock_engine)
        configs = await service.get("case", mock_user_res)

        assert "priority" in configs
        assert configs["priority"].options == {"low": "Low", "medium": "Medium", "high": "High"}


@pytest.mark.asyncio
async def test_configs_service_get_all(mock_engine):
    """Test getting all configs"""
    with patch('atlas_shared_app.services.atlas_configs_service.AtlasConfigsRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_all = AsyncMock(return_value=[
            AtlasConfigs(
                entity_type=f"type_{i}",
                field_name=f"field_{i}",
                options={f"option_{i}": f"Option {i}"},
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(3)
        ])

        service = AtlasConfigsService(mock_engine)
        all_configs = await service.get_all()

        assert len(all_configs) == 3


@pytest.mark.asyncio
async def test_configs_service_get_by_entity_type(mock_engine, mock_user_res):
    """Test getting configs by entity type"""
    with patch('atlas_shared_app.services.atlas_configs_service.AtlasConfigsRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_entity_type = AsyncMock(return_value=[
            AtlasConfigs(
                entity_type="same_type",
                field_name=f"field_{i}",
                options={"option1": "Option 1", "option2": "Option 2"},
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(3)
        ])

        service = AtlasConfigsService(mock_engine)
        configs = await service.get_by_entity_type("same_type", mock_user_res)

        assert len(configs) == 3


@pytest.mark.asyncio
async def test_configs_service_create(mock_engine, sample_config, mock_user_res):
    """Test creating a new config"""
    with patch('atlas_shared_app.services.atlas_configs_service.AtlasConfigsRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        created_config = AtlasConfigs(
            entity_type="case",
            field_name="priority",
            options={"low": "Low", "medium": "Medium", "high": "High"},
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        )
        mock_repo.create = AsyncMock(return_value=created_config)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasConfigsService(mock_engine)
        result = await service.create(sample_config, mock_user_res)

        assert result == created_config
        mock_repo.create.assert_called_once()
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_configs_service_update(mock_engine, mock_user_res):
    """Test updating a config"""
    with patch('atlas_shared_app.services.atlas_configs_service.AtlasConfigsRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        updated_config = AtlasConfigs(
            entity_type="case",
            field_name="priority",
            options={"low": "Low", "medium": "Medium", "high": "High", "critical": "Critical"},
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        )
        mock_repo.update = AsyncMock(return_value=updated_config)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasConfigsService(mock_engine)
        result = await service.update("case", "priority", {"options": {"low": "Low", "medium": "Medium", "high": "High", "critical": "Critical"}}, mock_user_res)

        assert result == updated_config
        mock_repo.update.assert_called_once()
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_configs_service_delete(mock_engine, mock_user_res):
    """Test deleting a config"""
    with patch('atlas_shared_app.services.atlas_configs_service.AtlasConfigsRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.delete = AsyncMock(return_value=True)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasConfigsService(mock_engine)
        result = await service.delete("case", "priority", mock_user_res)

        assert result is True
        mock_repo.delete.assert_called_once_with("case", "priority")
        mock_history_service.create_silently.assert_called_once()
