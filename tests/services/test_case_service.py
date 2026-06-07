"""Tests for AtlasCaseService"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel import SQLModel, Field

from atlas_shared_app.services.atlas_case_service import AtlasCaseService, CaseValidationError
from atlas_shared_app.entities.atlas_case import AtlasCase, AtlasCaseBase, AtlasCaseReq, AtlasCaseStatus, AtlasCaseStatusReq
from atlas_shared_app.settings.atlas_case_settings import AtlasCaseSettings


class SampleCaseModel(SQLModel):
    """Sample SQLModel for testing validation"""
    field1: str = Field()
    field2: int = Field()


@pytest.fixture
def mock_engine():
    return MagicMock()


@pytest.fixture
def service(mock_engine):
    return AtlasCaseService(mock_engine)


@pytest.fixture
def mock_user():
    """Create a mock user with required attributes"""
    user = MagicMock()
    user.user_id = "user-1"
    user.user_name = "Test User"
    return user


@pytest.fixture
def case_settings():
    return AtlasCaseSettings(case_types={"support": SampleCaseModel})


@pytest.fixture
def sample_case():
    return AtlasCase(
        case_id="case-123",
        case_type="support",
        title="Test Case",
        data={"field1": "value1", "field2": 123},
        case_status=AtlasCaseStatus.DRAFT,
        assigned_user_id="user-2",
        assigned_user_name="Assigned User",
        client_id="client-1",
        client_name="Test Client",
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


def test_service_init(mock_engine):
    """Test service initialization"""
    service = AtlasCaseService(mock_engine)
    assert service.repository is not None


@pytest.mark.asyncio
async def test_get_by_id(service, sample_case, mock_user):
    """Test getting a case by ID"""
    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=sample_case)

        result = await service.get_by_id("case-123", mock_user)

        assert result == sample_case
        mock_repo.get_by_id.assert_called_once_with("case-123")


@pytest.mark.asyncio
async def test_get_all(service, sample_case):
    """Test getting all cases"""
    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_all = AsyncMock(return_value=[sample_case])

        result = await service.get_all(skip=0, limit=100)

        assert len(result) == 1
        mock_repo.get_all.assert_called_once_with(skip=0, limit=100, case_status=None, client_id=None, entity_type=None, entity_id=None, assigned_user_id=None)


@pytest.mark.asyncio
async def test_get_all_with_filters(service, sample_case):
    """Test getting all cases with filters"""
    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_all = AsyncMock(return_value=[sample_case])

        result = await service.get_all(skip=0, limit=100, case_status="DRAFT", client_id="client-1")

        assert len(result) == 1
        mock_repo.get_all.assert_called_once_with(skip=0, limit=100, case_status="DRAFT", client_id="client-1", entity_type=None, entity_id=None, assigned_user_id=None)


@pytest.mark.asyncio
async def test_delete_case_not_found(service, mock_user):
    """Test deleting a non-existent case"""
    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=None)
        mock_repo.delete = AsyncMock(return_value=False)
        mock_repo.engine = MagicMock()

        result = await service.delete("nonexistent", mock_user)

        assert result is False


@pytest.mark.asyncio
async def test_get_by_client_id(service, sample_case, mock_user):
    """Test getting cases by client ID"""
    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_by_client_id = AsyncMock(return_value=[sample_case])

        result = await service.get_by_client_id("client-1", mock_user)

        assert len(result) == 1
        mock_repo.get_by_client_id.assert_called_once_with("client-1")


@pytest.mark.asyncio
async def test_get_by_assigned_user_id(service, sample_case, mock_user):
    """Test getting cases by assigned user ID"""
    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_by_assigned_user_id = AsyncMock(return_value=[sample_case])

        result = await service.get_by_assigned_user_id("user-2", mock_user)

        assert len(result) == 1
        mock_repo.get_by_assigned_user_id.assert_called_once_with("user-2", client_id=None)


@pytest.mark.asyncio
async def test_get_by_status(service, sample_case, mock_user):
    """Test getting cases by status"""
    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_by_status = AsyncMock(return_value=[sample_case])

        result = await service.get_by_status(AtlasCaseStatus.DRAFT, mock_user)

        assert len(result) == 1
        mock_repo.get_by_status.assert_called_once_with(AtlasCaseStatus.DRAFT, client_id=None)


@pytest.mark.asyncio
async def test_update_status_not_found(service, mock_user):
    """Test updating status of non-existent case"""
    status_req = AtlasCaseStatusReq(
        case_status=AtlasCaseStatus.SUBMITTED,
        assigned_user_id="user-2",
        assigned_user_name="Assigned User",
        remark=""
    )

    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as exc_info:
            await service.update_status("nonexistent", status_req, mock_user)

        assert "does not exist" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_status_update_fails(service, sample_case, mock_user):
    """Test updating case status when update fails"""
    status_req = AtlasCaseStatusReq(
        case_status=AtlasCaseStatus.SUBMITTED,
        assigned_user_id="user-2",
        assigned_user_name="Assigned User",
        remark=""
    )

    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=sample_case)
        mock_repo.update = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as exc_info:
            await service.update_status("case-123", status_req, mock_user)

        assert "Failed to update" in str(exc_info.value)


def test_validate_model_success(case_settings):
    """Test validate_model with valid data"""
    data = {"field1": "value", "field2": 123}

    result = AtlasCaseService.validate_model("support", data, case_settings)

    assert result is True


def test_validate_model_invalid_data(case_settings):
    """Test validate_model with invalid data"""
    data = {"field1": "value", "field2": "not_an_int"}

    with pytest.raises(CaseValidationError) as exc_info:
        AtlasCaseService.validate_model("support", data, case_settings)

    assert "field2" in exc_info.value.field_name


def test_validate_model_unknown_case_type():
    """Test validate_model with unknown case type"""
    settings = AtlasCaseSettings(case_types={})
    data = {"field1": "value"}

    with pytest.raises(KeyError):
        AtlasCaseService.validate_model("unknown", data, settings)


def test_case_validation_error():
    """Test CaseValidationError exception"""
    error = CaseValidationError("field_name", "error message")

    assert error.field_name == "field_name"
    assert error.error_message == "error message"
    assert "field_name" in str(error)
    assert "error message" in str(error)


@pytest.mark.asyncio
async def test_create_case(service, mock_user, case_settings):
    """Test creating a case"""
    case_base = AtlasCaseBase(
        case_type="support",
        title="New Case",
        data={"field1": "value", "field2": 123},
        client_id="client-1",
        assigned_user_id="user-2",
        assigned_user_name="Assigned User"
    )

    created_case = AtlasCase(
        case_id="case-new",
        case_type="support",
        title="New Case",
        data={"field1": "value", "field2": 123},
        case_status=AtlasCaseStatus.DRAFT,
        client_id="client-1",
        assigned_user_id="user-2",
        assigned_user_name="Assigned User",
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )

    with patch.object(service, 'repository') as mock_repo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo.create = AsyncMock(return_value=created_case)
        mock_repo.engine = MagicMock()
        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        result = await service.create(case_base, case_settings, mock_user)

        assert result == created_case
        mock_repo.create.assert_called_once()
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_update_case(service, sample_case, mock_user, case_settings):
    """Test updating a case"""
    case_req = AtlasCaseReq(
        case_type="support",
        title="Updated Case",
        data={"field1": "updated", "field2": 456},
        client_id="client-1",
        assigned_user_id="user-2",
        assigned_user_name="Assigned User"
    )

    with patch.object(service, 'repository') as mock_repo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo.get_by_id = AsyncMock(return_value=sample_case)
        mock_repo.update = AsyncMock(return_value=sample_case)
        mock_repo.engine = MagicMock()
        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        result = await service.update("case-123", case_req, case_settings, mock_user)

        assert result == sample_case
        mock_repo.get_by_id.assert_called_once_with("case-123")
        mock_repo.update.assert_called_once()
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_update_case_not_found(service, mock_user, case_settings):
    """Test updating a non-existent case"""
    case_req = AtlasCaseReq(
        case_type="support",
        title="Updated Case",
        data={"field1": "updated", "field2": 456},
        client_id="client-1",
        assigned_user_id="user-2",
        assigned_user_name="Assigned User"
    )

    with patch.object(service, 'repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as exc_info:
            await service.update("nonexistent", case_req, case_settings, mock_user)

        assert "does not exist" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_case_found(service, sample_case, mock_user):
    """Test deleting an existing case"""
    with patch.object(service, 'repository') as mock_repo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo.get_by_id = AsyncMock(return_value=sample_case)
        mock_repo.delete = AsyncMock(return_value=True)
        mock_repo.engine = MagicMock()
        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        result = await service.delete("case-123", mock_user)

        assert result is True
        mock_repo.delete.assert_called_once_with("case-123")
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_update_status_with_remark(service, sample_case, mock_user):
    """Test updating case status with a remark"""
    status_req = AtlasCaseStatusReq(
        case_status=AtlasCaseStatus.SUBMITTED,
        assigned_user_id="user-3",
        assigned_user_name="New Assignee",
        remark="Status changed to submitted"
    )

    updated_case = AtlasCase(
        case_id="case-123",
        case_type="support",
        title="Test Case",
        data={"field1": "value1", "field2": 123},
        case_status=AtlasCaseStatus.SUBMITTED,
        client_id="client-1",
        assigned_user_id="user-3",
        assigned_user_name="New Assignee",
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )

    with patch.object(service, 'repository') as mock_repo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService, \
         patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkService') as MockRemarkService:
        mock_repo.get_by_id = AsyncMock(return_value=sample_case)
        mock_repo.update = AsyncMock(return_value=updated_case)
        mock_repo.engine = MagicMock()

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        mock_remark_service = MockRemarkService.return_value
        mock_remark_service.create_silently = AsyncMock()

        result = await service.update_status("case-123", status_req, mock_user)

        assert result == updated_case
        mock_remark_service.create_silently.assert_called_once()
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_update_status_without_remark(service, sample_case, mock_user):
    """Test updating case status without a remark"""
    status_req = AtlasCaseStatusReq(
        case_status=AtlasCaseStatus.SUBMITTED,
        assigned_user_id="user-3",
        assigned_user_name="New Assignee",
        remark=""
    )

    updated_case = AtlasCase(
        case_id="case-123",
        case_type="support",
        title="Test Case",
        data={"field1": "value1", "field2": 123},
        case_status=AtlasCaseStatus.SUBMITTED,
        client_id="client-1",
        assigned_user_id="user-3",
        assigned_user_name="New Assignee",
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )

    with patch.object(service, 'repository') as mock_repo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService, \
         patch('atlas_shared_app.services.atlas_remark_service.AtlasRemarkService') as MockRemarkService:
        mock_repo.get_by_id = AsyncMock(return_value=sample_case)
        mock_repo.update = AsyncMock(return_value=updated_case)
        mock_repo.engine = MagicMock()

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        mock_remark_service = MockRemarkService.return_value
        mock_remark_service.create_silently = AsyncMock()

        result = await service.update_status("case-123", status_req, mock_user)

        assert result == updated_case
        # Remark service should NOT be called when remark is empty
        mock_remark_service.create_silently.assert_not_called()
        mock_history_service.create_silently.assert_called_once()


@pytest.mark.asyncio
async def test_has_non_closed_cases_for_entity(service):
    """Test checking if entity has non-closed cases"""
    with patch.object(service, 'repository') as mock_repo:
        mock_repo.has_non_closed_cases_for_entity = AsyncMock(return_value=True)

        result = await service.has_non_closed_cases_for_entity("client", "client-123")

        assert result is True
        mock_repo.has_non_closed_cases_for_entity.assert_called_once_with("client", "client-123")
