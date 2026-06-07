"""Tests for History service - unit tests without database"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from atlas_shared_app.entities import AtlasHistoryBase, UserRole, AppEnum
from atlas_shared_app.entities.atlas_user import AtlasUserBase
from atlas_shared_app.entities.atlas_history import AtlasHistory
from atlas_shared_app.services.atlas_history_service import AtlasHistoryService


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    from atlas_shared_app.entities.atlas_user import AtlasUserRes
    return AtlasUserRes(
        user_id="USER001",
        login_id="testuser",
        user_name="Test User",
        user_status="active",
        email="test@example.com",
        phone="+1234567890",
        internal=True,
        roles={AppEnum.ATLAS_APP_IDENTITY: UserRole.ADMIN},
        creater_id="USER001",
        creater_name="Test User",
        updater_id="USER001",
        updater_name="Test User",
    )


@pytest.fixture
def sample_history():
    """Create a sample history entry for testing"""
    return AtlasHistoryBase(
        history_id="",
        entity_type="case",
        entity_id="CASE001",
        action="CREATE",
        description="Case created for testing",
        internal_only=True,
    )


@pytest.fixture
def mock_engine():
    """Create a mock engine for testing"""
    return MagicMock()


def test_history_service_init(mock_engine):
    """Test HistoryService initialization"""
    with patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryRepository'):
        service = AtlasHistoryService(mock_engine)
        assert service.repository is not None


# Note: test_history_service_create is tested via integration tests as
# the service uses **history.__dict__ spread which requires actual database testing


@pytest.mark.asyncio
async def test_history_service_get_by_id(mock_engine, mock_user):
    """Test getting a history entry by ID"""
    with patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_id = AsyncMock(return_value=AtlasHistory(
            history_id="HIST001",
            entity_type="case",
            entity_id="CASE001",
            action="CREATE",
            description="Test",
            internal_only=True,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))

        service = AtlasHistoryService(mock_engine)
        fetched = await service.get_by_id("HIST001", mock_user)

        assert fetched is not None
        assert fetched.history_id == "HIST001"


@pytest.mark.asyncio
async def test_history_service_get_by_id_not_found(mock_engine, mock_user):
    """Test getting a non-existent history entry"""
    with patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_id = AsyncMock(return_value=None)

        service = AtlasHistoryService(mock_engine)
        fetched = await service.get_by_id("nonexistent_id", mock_user)

        assert fetched is None


@pytest.mark.asyncio
async def test_history_service_get_all(mock_engine):
    """Test getting all history entries"""
    with patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_all = AsyncMock(return_value=[
            AtlasHistory(
                history_id=f"HIST00{i}",
                entity_type="case",
                entity_id=f"CASE00{i}",
                action="CREATE",
                description=f"Test {i}",
                internal_only=True,
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(3)
        ])

        service = AtlasHistoryService(mock_engine)
        all_histories = await service.get_all()

        assert len(all_histories) == 3


@pytest.mark.asyncio
async def test_history_service_get_by_entity_id(mock_engine, mock_user):
    """Test getting history entries by reference ID"""
    with patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_entity_id = AsyncMock(return_value=[
            AtlasHistory(
                history_id=f"HIST00{i}",
                entity_type="case",
                entity_id="CASE001",
                action=["CREATE", "UPDATE", "DELETE"][i],
                description=f"Test {i}",
                internal_only=True,
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(3)
        ])

        service = AtlasHistoryService(mock_engine)
        histories = await service.get_by_entity_id("CASE001", mock_user)

        assert len(histories) == 3


@pytest.mark.asyncio
async def test_history_service_create_silently(mock_engine, mock_user, sample_history):
    """Test creating a history entry silently"""
    with patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.create = AsyncMock(return_value=AtlasHistory(
            history_id="HIST001",
            entity_type="case",
            entity_id="CASE001",
            action="CREATE",
            description="Test",
            internal_only=True,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))

        service = AtlasHistoryService(mock_engine)
        # Should not raise any exception and return None
        result = await service.create_silently(sample_history, mock_user)
        assert result is None


@pytest.mark.asyncio
async def test_history_service_create_silently_handles_error(mock_engine, mock_user, sample_history):
    """Test that create_silently doesn't raise errors"""
    with patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.create = AsyncMock(side_effect=Exception("Database error"))

        service = AtlasHistoryService(mock_engine)
        # Should not raise any exception
        result = await service.create_silently(sample_history, mock_user)
        assert result is None
