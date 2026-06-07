"""Tests for Document service"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from atlas_shared_app.entities import AtlasDocumentBase, UserRole, AppEnum
from atlas_shared_app.entities.atlas_user import AtlasUserRes
from atlas_shared_app.entities.atlas_document import AtlasDocument
from atlas_shared_app.services.atlas_document_service import AtlasDocumentService
from atlas_shared_app.settings.atlas_document_settings import AtlasDocumentSettings


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
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
def sample_document():
    """Create a sample document for testing"""
    return AtlasDocumentBase(
        document_id="",
        document_name="test_file.pdf",
        entity_type="case",
        entity_id="CASE001",
    )


@pytest.fixture
def mock_engine():
    """Create a mock engine for testing"""
    return MagicMock()


@pytest.fixture
def mock_document_settings():
    """Create mock document settings"""
    return AtlasDocumentSettings(bucket="test-bucket", project_id="test-project")


def test_document_service_init(mock_engine):
    """Test DocumentService initialization"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository'):
        service = AtlasDocumentService(mock_engine)
        assert service.repository is not None


@pytest.mark.asyncio
async def test_document_service_get_by_id(mock_engine, mock_user):
    """Test getting a document by ID"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_id = AsyncMock(return_value=AtlasDocument(
            document_id="DOC001",
            document_name="test_file.pdf",
            entity_type="case",
            entity_id="CASE001",
            bucket="test-bucket",
            fullpath="DOC001/test_file.pdf",
            internal_only=True,
            deleted=False,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))

        service = AtlasDocumentService(mock_engine)
        fetched = await service.get_by_id("DOC001", mock_user)

        assert fetched is not None
        assert fetched.document_id == "DOC001"
        assert fetched.document_name == "test_file.pdf"


@pytest.mark.asyncio
async def test_document_service_get_by_id_not_found(mock_engine, mock_user):
    """Test getting a non-existent document"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_id = AsyncMock(return_value=None)

        service = AtlasDocumentService(mock_engine)
        fetched = await service.get_by_id("nonexistent_id", mock_user)

        assert fetched is None


@pytest.mark.asyncio
async def test_document_service_get_all(mock_engine):
    """Test getting all documents"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_all = AsyncMock(return_value=[
            AtlasDocument(
                document_id=f"DOC00{i}",
                document_name=f"file_{i}.pdf",
                entity_type="case",
                entity_id=f"CASE00{i}",
                bucket="test-bucket",
                fullpath=f"DOC00{i}/file_{i}.pdf",
                internal_only=True,
                deleted=False,
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(3)
        ])

        service = AtlasDocumentService(mock_engine)
        all_docs = await service.get_all()

        assert len(all_docs) == 3


@pytest.mark.asyncio
async def test_document_service_get_all_with_pagination(mock_engine):
    """Test getting all documents with pagination"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_all = AsyncMock(return_value=[
            AtlasDocument(
                document_id=f"DOC00{i}",
                document_name=f"file_{i}.pdf",
                entity_type="case",
                entity_id=f"CASE00{i}",
                bucket="test-bucket",
                fullpath=f"DOC00{i}/file_{i}.pdf",
                internal_only=True,
                deleted=False,
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(2)
        ])

        service = AtlasDocumentService(mock_engine)
        docs = await service.get_all(skip=0, limit=2)

        assert len(docs) == 2


@pytest.mark.asyncio
async def test_document_service_get_by_entity_id(mock_engine, mock_user):
    """Test getting documents by reference ID"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_by_entity_id = AsyncMock(return_value=[
            AtlasDocument(
                document_id=f"DOC00{i}",
                document_name=f"file_{i}.pdf",
                entity_type="case",
                entity_id="CASE001",
                bucket="test-bucket",
                fullpath=f"DOC00{i}/file_{i}.pdf",
                internal_only=True,
                deleted=False,
                creater_id="USER001",
                creater_name="Test User",
                updater_id="USER001",
                updater_name="Test User",
            ) for i in range(3)
        ])

        service = AtlasDocumentService(mock_engine)
        docs = await service.get_by_entity_id("CASE001", mock_user)

        assert len(docs) == 3


@pytest.mark.asyncio
async def test_document_service_update(mock_engine, mock_user):
    """Test updating a document"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.get_by_id = AsyncMock(return_value=AtlasDocument(
            document_id="DOC001",
            document_name="test_file.pdf",
            entity_type="case",
            entity_id="CASE001",
            bucket="test-bucket",
            fullpath="DOC001/test_file.pdf",
            internal_only=True,
            deleted=False,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))
        mock_repo.update = AsyncMock(return_value=AtlasDocument(
            document_id="DOC001",
            document_name="updated_file.pdf",
            entity_type="case",
            entity_id="CASE001",
            bucket="test-bucket",
            fullpath="DOC001/updated_file.pdf",
            internal_only=False,
            deleted=False,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasDocumentService(mock_engine)
        updated = await service.update("DOC001", {"document_name": "updated_file.pdf"}, mock_user)

        assert updated is not None
        assert updated.document_name == "updated_file.pdf"


@pytest.mark.asyncio
async def test_document_service_delete(mock_engine, mock_user):
    """Test deleting a document"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.get_by_id = AsyncMock(return_value=AtlasDocument(
            document_id="DOC001",
            document_name="test_file.pdf",
            entity_type="case",
            entity_id="CASE001",
            bucket="test-bucket",
            fullpath="DOC001/test_file.pdf",
            internal_only=True,
            deleted=False,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))
        mock_repo.delete = AsyncMock(return_value=True)

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasDocumentService(mock_engine)
        result = await service.delete("DOC001", mock_user)

        assert result is True


@pytest.mark.asyncio
async def test_document_service_delete_not_found(mock_engine, mock_user):
    """Test deleting a non-existent document"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.get_by_id = AsyncMock(return_value=None)
        mock_repo.delete = AsyncMock(return_value=False)

        service = AtlasDocumentService(mock_engine)
        result = await service.delete("nonexistent_id", mock_user)

        assert result is False


@pytest.mark.asyncio
async def test_document_service_create(mock_engine, mock_user, mock_document_settings):
    """Test creating a document"""
    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.create = AsyncMock(return_value=AtlasDocument(
            document_id="DOC001",
            document_name="test_file.pdf",
            entity_type="case",
            entity_id="CASE001",
            bucket="test-bucket",
            fullpath="DOC001/test_file.pdf",
            internal_only=True,
            deleted=False,
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasDocumentService(mock_engine)
        document_base = AtlasDocumentBase(
            document_name="test_file.pdf",
            entity_type="case",
            entity_id="CASE001",
        )

        created = await service.create(document_base, mock_document_settings, mock_user)

        assert created is not None
        assert created.document_id == "DOC001"
        assert created.document_name == "test_file.pdf"
        mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_document_service_create_with_client_from_user(mock_engine, mock_document_settings):
    """Test creating a document sets client info from user when not provided"""
    user_with_client = AtlasUserRes(
        user_id="USER001",
        login_id="testuser",
        user_name="Test User",
        user_status="active",
        email="test@example.com",
        phone="+1234567890",
        internal=False,
        client_id="CLIENT001",
        client_name="Test Client",
        roles={},
        creater_id="USER001",
        creater_name="Test User",
        updater_id="USER001",
        updater_name="Test User",
    )

    with patch('atlas_shared_app.services.atlas_document_service.AtlasDocumentRepository') as MockRepo, \
         patch('atlas_shared_app.services.atlas_history_service.AtlasHistoryService') as MockHistoryService:
        mock_repo = MockRepo.return_value
        mock_repo.engine = mock_engine
        mock_repo.create = AsyncMock(return_value=AtlasDocument(
            document_id="DOC001",
            document_name="test_file.pdf",
            entity_type="case",
            entity_id="CASE001",
            bucket="test-bucket",
            fullpath="DOC001/test_file.pdf",
            internal_only=True,
            deleted=False,
            client_id="CLIENT001",
            client_name="Test Client",
            creater_id="USER001",
            creater_name="Test User",
            updater_id="USER001",
            updater_name="Test User",
        ))

        mock_history_service = MockHistoryService.return_value
        mock_history_service.create_silently = AsyncMock()

        service = AtlasDocumentService(mock_engine)
        document_base = AtlasDocumentBase(
            document_name="test_file.pdf",
            entity_type="case",
            entity_id="CASE001",
        )

        created = await service.create(document_base, mock_document_settings, user_with_client)

        assert created is not None
        assert created.client_id == "CLIENT001"
        assert created.client_name == "Test Client"
