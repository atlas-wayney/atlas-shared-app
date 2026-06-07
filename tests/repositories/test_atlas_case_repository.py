"""Tests for AtlasCaseRepository"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncEngine

from atlas_shared_app.repositories.atlas_case_repository import AtlasCaseRepository
from atlas_shared_app.entities.atlas_case import AtlasCase, AtlasCaseStatus


@pytest.fixture
def mock_engine():
    return MagicMock(spec=AsyncEngine)


@pytest.fixture
def repository(mock_engine):
    return AtlasCaseRepository(mock_engine)


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
        assigned_user_id="user-2",
        assigned_user_name="Assigned User",
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


@pytest.mark.asyncio
async def test_repository_init(mock_engine):
    """Test repository initialization"""
    repo = AtlasCaseRepository(mock_engine)
    assert repo.engine == mock_engine


@pytest.mark.asyncio
async def test_create_case(repository, sample_case):
    """Test creating a case"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await repository.create(sample_case)

        mock_session.add.assert_called_once_with(sample_case)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_case)
        assert result == sample_case


@pytest.mark.asyncio
async def test_get_by_id_found(repository, sample_case):
    """Test getting a case by ID when found"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_case
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id("case-123")

        assert result == sample_case
        mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository):
    """Test getting a case by ID when not found"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id("nonexistent")

        assert result is None


@pytest.mark.asyncio
async def test_get_all_no_filters(repository, sample_case):
    """Test getting all cases without filters"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_case]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100)

        assert len(result) == 1
        assert result[0] == sample_case


@pytest.mark.asyncio
async def test_get_all_with_status_filter(repository, sample_case):
    """Test getting all cases with status filter"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_case]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100, case_status="DRAFT")

        assert len(result) == 1


@pytest.mark.asyncio
async def test_get_all_with_client_filter(repository, sample_case):
    """Test getting all cases with client filter"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_case]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100, client_id="client-1")

        assert len(result) == 1


@pytest.mark.asyncio
async def test_get_all_with_both_filters(repository, sample_case):
    """Test getting all cases with both status and client filters"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_case]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100, case_status="DRAFT", client_id="client-1")

        assert len(result) == 1


@pytest.mark.asyncio
async def test_update_case(repository, sample_case):
    """Test updating a case"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await repository.update(sample_case)

        mock_session.add.assert_called_once_with(sample_case)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_case)
        assert result == sample_case


@pytest.mark.asyncio
async def test_delete_found(repository, sample_case):
    """Test deleting a case when found"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_case
        mock_session.execute.return_value = mock_result

        result = await repository.delete("case-123")

        assert result is True
        mock_session.delete.assert_called_once_with(sample_case)
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(repository):
    """Test deleting a case when not found"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.delete("nonexistent")

        assert result is False


@pytest.mark.asyncio
async def test_get_by_client_id(repository, sample_case):
    """Test getting cases by client ID"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_case]
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_client_id("client-1")

        assert len(result) == 1
        assert result[0] == sample_case


@pytest.mark.asyncio
async def test_get_by_assigned_user_id(repository, sample_case):
    """Test getting cases by assigned user ID"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_case]
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_assigned_user_id("user-2")

        assert len(result) == 1
        assert result[0] == sample_case


@pytest.mark.asyncio
async def test_get_by_status(repository, sample_case):
    """Test getting cases by status"""
    with patch('atlas_shared_app.repositories.atlas_case_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_case]
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_status(AtlasCaseStatus.DRAFT)

        assert len(result) == 1
        assert result[0] == sample_case
