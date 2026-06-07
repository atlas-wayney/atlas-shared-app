"""Tests for AtlasHistoryRepository"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncEngine

from atlas_shared_app.repositories.atlas_history_repository import AtlasHistoryRepository
from atlas_shared_app.entities.atlas_history import AtlasHistory


@pytest.fixture
def mock_engine():
    return MagicMock(spec=AsyncEngine)


@pytest.fixture
def repository(mock_engine):
    return AtlasHistoryRepository(mock_engine)


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


@pytest.mark.asyncio
async def test_repository_init(mock_engine):
    """Test repository initialization"""
    repo = AtlasHistoryRepository(mock_engine)
    assert repo.engine == mock_engine


@pytest.mark.asyncio
async def test_create_history(repository, sample_history):
    """Test creating a history entry"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await repository.create(sample_history)

        mock_session.add.assert_called_once_with(sample_history)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_history)
        assert result == sample_history


@pytest.mark.asyncio
async def test_get_by_id_found(repository, sample_history):
    """Test getting a history entry by ID when found"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_history
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id("history-123")

        assert result == sample_history
        mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository):
    """Test getting a history entry by ID when not found"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id("nonexistent")

        assert result is None


@pytest.mark.asyncio
async def test_get_all(repository, sample_history):
    """Test getting all history entries with pagination"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100)

        assert len(result) == 1
        assert result[0] == sample_history


@pytest.mark.asyncio
async def test_update_found(repository, sample_history):
    """Test updating a history entry when found"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_history
        mock_session.execute.return_value = mock_result

        update_data = {"description": "Updated description"}
        result = await repository.update("history-123", update_data)

        assert result == sample_history
        assert sample_history.description == "Updated description"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(repository):
    """Test updating a history entry when not found"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.update("nonexistent", {"description": "test"})

        assert result is None


@pytest.mark.asyncio
async def test_delete_found(repository, sample_history):
    """Test deleting a history entry when found"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_history
        mock_session.execute.return_value = mock_result

        result = await repository.delete("history-123")

        assert result is True
        mock_session.delete.assert_called_once_with(sample_history)
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(repository):
    """Test deleting a history entry when not found"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.delete("nonexistent")

        assert result is False


@pytest.mark.asyncio
async def test_get_by_entity_id(repository, sample_history):
    """Test getting history entries by entity ID"""
    with patch('atlas_shared_app.repositories.atlas_history_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_history]
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_entity_id("case-456")

        assert len(result) == 1
        assert result[0] == sample_history
