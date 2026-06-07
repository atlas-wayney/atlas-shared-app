"""Tests for AtlasRemarkRepository"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncEngine

from atlas_shared_app.repositories.atlas_remark_repository import AtlasRemarkRepository
from atlas_shared_app.entities.atlas_remark import AtlasRemark


@pytest.fixture
def mock_engine():
    return MagicMock(spec=AsyncEngine)


@pytest.fixture
def repository(mock_engine):
    return AtlasRemarkRepository(mock_engine)


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


@pytest.mark.asyncio
async def test_repository_init(mock_engine):
    """Test repository initialization"""
    repo = AtlasRemarkRepository(mock_engine)
    assert repo.engine == mock_engine


@pytest.mark.asyncio
async def test_create_remark(repository, sample_remark):
    """Test creating a remark"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await repository.create(sample_remark)

        mock_session.add.assert_called_once_with(sample_remark)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_remark)
        assert result == sample_remark


@pytest.mark.asyncio
async def test_get_by_id_found(repository, sample_remark):
    """Test getting a remark by ID when found"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_remark
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id("remark-123")

        assert result == sample_remark
        mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository):
    """Test getting a remark by ID when not found"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id("nonexistent")

        assert result is None


@pytest.mark.asyncio
async def test_get_all(repository, sample_remark):
    """Test getting all remarks with pagination"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_remark]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100)

        assert len(result) == 1
        assert result[0] == sample_remark


@pytest.mark.asyncio
async def test_update_found(repository, sample_remark):
    """Test updating a remark when found"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_remark
        mock_session.execute.return_value = mock_result

        update_data = {"remark": "Updated remark"}
        result = await repository.update("remark-123", update_data)

        assert result == sample_remark
        assert sample_remark.remark == "Updated remark"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(repository):
    """Test updating a remark when not found"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.update("nonexistent", {"remark": "test"})

        assert result is None


@pytest.mark.asyncio
async def test_delete_found(repository, sample_remark):
    """Test deleting a remark when found"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_remark
        mock_session.execute.return_value = mock_result

        result = await repository.delete("remark-123")

        assert result is True
        mock_session.delete.assert_called_once_with(sample_remark)
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(repository):
    """Test deleting a remark when not found"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.delete("nonexistent")

        assert result is False


@pytest.mark.asyncio
async def test_get_by_entity_id(repository, sample_remark):
    """Test getting remarks by entity ID"""
    with patch('atlas_shared_app.repositories.atlas_remark_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_remark]
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_entity_id("case-456")

        assert len(result) == 1
        assert result[0] == sample_remark
