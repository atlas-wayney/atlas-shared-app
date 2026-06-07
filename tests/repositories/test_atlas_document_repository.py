"""Tests for AtlasDocumentRepository"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncEngine

from atlas_shared_app.repositories.atlas_document_repository import AtlasDocumentRepository
from atlas_shared_app.entities.atlas_document import AtlasDocument


@pytest.fixture
def mock_engine():
    return MagicMock(spec=AsyncEngine)


@pytest.fixture
def repository(mock_engine):
    return AtlasDocumentRepository(mock_engine)


@pytest.fixture
def sample_document():
    return AtlasDocument(
        document_id="doc-123",
        document_name="test.pdf",
        entity_type="case",
        entity_id="case-456",
        bucket="test-bucket",
        fullpath="/path/to/test.pdf",
        internal_only=False,
        deleted=False,
        creater_id="user-1",
        creater_name="Test User",
        updater_id="user-1",
        updater_name="Test User"
    )


@pytest.mark.asyncio
async def test_repository_init(mock_engine):
    """Test repository initialization"""
    repo = AtlasDocumentRepository(mock_engine)
    assert repo.engine == mock_engine


@pytest.mark.asyncio
async def test_create_document(repository, sample_document):
    """Test creating a document"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await repository.create(sample_document)

        mock_session.add.assert_called_once_with(sample_document)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_document)
        assert result == sample_document


@pytest.mark.asyncio
async def test_get_by_id_found(repository, sample_document):
    """Test getting a document by ID when found"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_document
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id("doc-123")

        assert result == sample_document
        mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository):
    """Test getting a document by ID when not found"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id("nonexistent")

        assert result is None


@pytest.mark.asyncio
async def test_get_all(repository, sample_document):
    """Test getting all documents with pagination"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_document]
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=100)

        assert len(result) == 1
        assert result[0] == sample_document


@pytest.mark.asyncio
async def test_update_found(repository, sample_document):
    """Test updating a document when found"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_document
        mock_session.execute.return_value = mock_result

        update_data = {"document_name": "updated.pdf"}
        result = await repository.update("doc-123", update_data)

        assert result == sample_document
        assert sample_document.document_name == "updated.pdf"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(repository):
    """Test updating a document when not found"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.update("nonexistent", {"file_name": "test"})

        assert result is None


@pytest.mark.asyncio
async def test_delete_found(repository, sample_document):
    """Test deleting a document when found"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_document
        mock_session.execute.return_value = mock_result

        result = await repository.delete("doc-123")

        assert result is True
        mock_session.delete.assert_called_once_with(sample_document)
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(repository):
    """Test deleting a document when not found"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.delete("nonexistent")

        assert result is False


@pytest.mark.asyncio
async def test_get_by_entity_id(repository, sample_document):
    """Test getting documents by entity ID"""
    with patch('atlas_shared_app.repositories.atlas_document_repository.AsyncSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_document]
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_entity_id("case-456")

        assert len(result) == 1
        assert result[0] == sample_document
