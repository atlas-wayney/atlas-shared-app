"""Tests for Remark service - unit tests without database"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from atlas_shared_app.entities import AtlasRemarkBase
from atlas_shared_app.entities.atlas_remark import AtlasRemark
from atlas_shared_app.services.atlas_remark_service import AtlasRemarkService


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
        roles={},
        creater_id="USER001",
        creater_name="Test User",
        updater_id="USER001",
        updater_name="Test User"
    )


@pytest.fixture
def sample_remark():
    """Create a sample remark for testing"""
    return AtlasRemarkBase(
        entity_type="case",
        entity_id="CASE001",
        remark="This is a test remark",
        internal_only=True,
    )


@pytest.fixture
def mock_engine():
    """Create a mock engine for testing"""
    return MagicMock()


def test_remark_service_init(mock_engine):
    """Test RemarkService initialization"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository'):
        service = AtlasRemarkService(mock_engine)
        assert service.repository is not None


@pytest.mark.asyncio
async def test_remark_service_get_by_id(mock_engine, mock_user):
    """Test getting a remark by ID"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_id = AsyncMock(return_value=AtlasRemark(
            remark_id="REM001",
            entity_type="case",
            entity_id="CASE001",
            remark="Test remark",
            internal_only=True,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))

        service = AtlasRemarkService(mock_engine)
        fetched = await service.get_by_id("REM001", mock_user)

        assert fetched is not None
        assert fetched.remark_id == "REM001"


@pytest.mark.asyncio
async def test_remark_service_get_by_id_not_found(mock_engine, mock_user):
    """Test getting a non-existent remark"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_id = AsyncMock(return_value=None)

        service = AtlasRemarkService(mock_engine)
        fetched = await service.get_by_id("nonexistent_id", mock_user)

        assert fetched is None


@pytest.mark.asyncio
async def test_remark_service_get_all(mock_engine):
    """Test getting all remarks"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_all = AsyncMock(return_value=[
            AtlasRemark(
                remark_id=f"REM00{i}",
                entity_type="case",
                entity_id=f"CASE00{i}",
                remark=f"Remark {i}",
                internal_only=True,
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(3)
        ])

        service = AtlasRemarkService(mock_engine)
        all_remarks = await service.get_all()

        assert len(all_remarks) == 3


@pytest.mark.asyncio
async def test_remark_service_get_by_entity_id(mock_engine, mock_user):
    """Test getting remarks by reference ID"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_entity_id = AsyncMock(return_value=[
            AtlasRemark(
                remark_id=f"REM00{i}",
                entity_type="case",
                entity_id="CASE001",
                remark=f"Remark {i}",
                internal_only=True,
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(3)
        ])

        service = AtlasRemarkService(mock_engine)
        remarks = await service.get_by_entity_id("CASE001", mock_user)

        assert len(remarks) == 3


@pytest.mark.asyncio
async def test_remark_service_create_silently_handles_error(mock_engine, mock_user, sample_remark):
    """Test that create_silently doesn't raise errors"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.create = AsyncMock(side_effect=Exception("Database error"))

        service = AtlasRemarkService(mock_engine)
        # Should not raise any exception
        result = await service.create_silently(sample_remark, mock_user)
        assert result is None


@pytest.mark.asyncio
async def test_remark_service_create_with_history(mock_engine, mock_user, sample_remark):
    """Test creating a remark with history logging"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        created_remark = AtlasRemark(
            remark_id="REM001",
            entity_type="case",
            entity_id="CASE001",
            remark="Test remark",
            internal_only=True,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        )
        mock_repo.create = AsyncMock(return_value=created_remark)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasRemarkService(mock_engine)
        result = await service.create(sample_remark, mock_user, log_history=True)

        assert result == created_remark
        mock_repo.create.assert_called_once()
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_remark_service_create_without_history(mock_engine, mock_user, sample_remark):
    """Test creating a remark without history logging"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        created_remark = AtlasRemark(
            remark_id="REM001",
            entity_type="case",
            entity_id="CASE001",
            remark="Test remark",
            internal_only=True,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        )
        mock_repo.create = AsyncMock(return_value=created_remark)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasRemarkService(mock_engine)
        result = await service.create(sample_remark, mock_user, log_history=False)

        assert result == created_remark
        mock_repo.create.assert_called_once()
        # History service should NOT be called when log_history is False
        mock_history_service.create_silently.assert_not_called()


@pytest.mark.asyncio
async def test_remark_service_create_long_remark_truncated_in_history(mock_engine, mock_user):
    """Test that long remarks are truncated in history description"""
    long_remark = AtlasRemarkBase(
        entity_type="case",
        entity_id="CASE001",
        remark="This is a very long remark that exceeds fifty characters and should be truncated in the history description",
        internal_only=True,
    )

    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        created_remark = AtlasRemark(
            remark_id="REM001",
            entity_type="case",
            entity_id="CASE001",
            remark=long_remark.remark,
            internal_only=True,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        )
        mock_repo.create = AsyncMock(return_value=created_remark)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasRemarkService(mock_engine)
        await service.create(long_remark, mock_user, log_history=True)

        # Check that history was called with truncated description
        mock_history_service.create_silently.assert_called_once()
        history_call_args = mock_history_service.create_silently.call_args[0][0]
        assert "..." in history_call_args.description


@pytest.mark.asyncio
async def test_remark_service_delete_found(mock_engine, mock_user):
    """Test deleting an existing remark"""
    existing_remark = AtlasRemark(
        remark_id="REM001",
        entity_type="case",
        entity_id="CASE001",
        remark="Test remark",
        internal_only=True,
        creater_id="USER001",
        creater_name="Test User",
        updater_id="USER001",
        updater_name="Test User",
    )

    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.get_by_id = AsyncMock(return_value=existing_remark)
        mock_repo.delete = AsyncMock(return_value=True)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasRemarkService(mock_engine)
        result = await service.delete("REM001", mock_user)

        assert result is True
        mock_repo.delete.assert_called_once_with("REM001")
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_remark_service_delete_not_found(mock_engine, mock_user):
    """Test deleting a non-existent remark"""
    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.get_by_id = AsyncMock(return_value=None)
        mock_repo.delete = AsyncMock(return_value=False)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasRemarkService(mock_engine)
        result = await service.delete("nonexistent", mock_user)

        assert result is False
        # History should NOT be logged if remark was not found
        mock_history_service.create_silently.assert_not_called()


@pytest.mark.asyncio
async def test_remark_service_delete_long_remark_truncated_in_history(mock_engine, mock_user):
    """Test that long remarks are truncated in history when deleting"""
    existing_remark = AtlasRemark(
        remark_id="REM001",
        entity_type="case",
        entity_id="CASE001",
        remark="This is a very long remark that exceeds fifty characters and should be truncated in the history description",
        internal_only=True,
        creater_id="USER001",
        creater_name="Test User",
        updater_id="USER001",
        updater_name="Test User",
    )

    with patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.get_by_id = AsyncMock(return_value=existing_remark)
        mock_repo.delete = AsyncMock(return_value=True)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasRemarkService(mock_engine)
        await service.delete("REM001", mock_user)

        # Check that history was called with truncated description
        mock_history_service.create_silently.assert_called_once()
        history_call_args = mock_history_service.create_silently.call_args[0][0]
        assert "..." in history_call_args.description
