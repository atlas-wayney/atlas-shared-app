"""Tests for AtlasConfigsRepository"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncEngine

from atlas_shared_app.repositories.atlas_configs_repository import AtlasConfigsRepository
from atlas_shared_app.entities.atlas_configs import AtlasConfigs


@pytest.fixture
def mock_engine():
    return MagicMock(spec=AsyncEngine)


@pytest.fixture
def repository(mock_engine):
    return AtlasConfigsRepository(mock_engine)


@pytest.fixture
def sample_config():
    return AtlasConfigs(
        entity_type="case",
        field_name="status",
        options=["DRAFT", "SUBMITTED", "CLOSED"],
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


@pytest.mark.asyncio
async def test_repository_init(mock_engine):
    """Test repository initialization"""
    repo = AtlasConfigsRepository(mock_engine)
    assert repo.engine == mock_engine


@pytest.mark.asyncio
async def test_create_config(repository, sample_config):
    """Test creating a config"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await repository.create(sample_config)

        mock_session.add.assert_called_once_with(sample_config)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_config)
        assert result == sample_config


@pytest.mark.asyncio
async def test_get_all(repository, sample_config):
    """Test getting all configs with pagination"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_config]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100)

        assert len(result) == 1
        assert result[0] == sample_config


@pytest.mark.asyncio
async def test_get(repository, sample_config):
    """Test getting configs by config type as dict"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_config]
        mock_session.execute.return_value = mock_result

        result = await repository.get("case")

        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == sample_config


@pytest.mark.asyncio
async def test_update_found(repository, sample_config):
    """Test updating an existing config"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_config
        mock_session.execute.return_value = mock_result

        result = await repository.update("case", "status", {"options": ["NEW", "OLD"]})

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result == sample_config


@pytest.mark.asyncio
async def test_update_not_found(repository):
    """Test updating a non-existent config"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.update("nonexistent", "field", {"options": ["NEW"]})

        assert result is None


@pytest.mark.asyncio
async def test_update_skips_protected_fields(repository, sample_config):
    """Test that update skips entity_type and field_name"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_config
        mock_session.execute.return_value = mock_result

        original_type = sample_config.entity_type
        original_field = sample_config.field_name

        await repository.update("case", "status", {
            "entity_type": "should_not_change",
            "field_name": "should_not_change",
            "options": ["NEW"]
        })

        # These should not have changed
        assert sample_config.entity_type == original_type
        assert sample_config.field_name == original_field


@pytest.mark.asyncio
async def test_delete_found(repository, sample_config):
    """Test deleting an existing config"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_config
        mock_session.execute.return_value = mock_result

        result = await repository.delete("case", "status")

        mock_session.delete.assert_called_once_with(sample_config)
        mock_session.commit.assert_called_once()
        assert result is True


@pytest.mark.asyncio
async def test_delete_not_found(repository):
    """Test deleting a non-existent config"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.delete("nonexistent", "field")

        assert result is False


@pytest.mark.asyncio
async def test_get_by_entity_type(repository, sample_config):
    """Test getting configs by entity type"""
    with patch('atlas_shared_app.repositories.atlas_configs_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_config]
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_entity_type("case")

        assert len(result) == 1
        assert result[0] == sample_config
