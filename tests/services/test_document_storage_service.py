"""Tests for AtlasDocumentStorageService"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import timedelta
from io import BytesIO

from atlas_shared_app.services.atlas_document_storage_service import AtlasDocumentStorageService
from atlas_shared_app.settings.atlas_document_settings import AtlasDocumentSettings


@pytest.fixture
def settings():
    return AtlasDocumentSettings(
        bucket="test-bucket",
        project_id="test-project",
        credentials_path="",
        signed_url_expiration=3600
    )


@pytest.fixture
def settings_with_credentials():
    return AtlasDocumentSettings(
        bucket="test-bucket",
        project_id="test-project",
        credentials_path="/path/to/credentials.json",
        signed_url_expiration=3600
    )


@pytest.fixture
def service(settings):
    return AtlasDocumentStorageService(settings)


@pytest.fixture
def mock_blob():
    blob = MagicMock()
    blob.name = "test-file.pdf"
    blob.size = 1024
    blob.content_type = "application/pdf"
    blob.time_created = "2024-01-01T00:00:00Z"
    blob.updated = "2024-01-01T00:00:00Z"
    blob.md5_hash = "abc123"
    blob.etag = "etag123"
    blob.exists.return_value = True
    return blob


def test_service_init(settings):
    """Test service initialization"""
    service = AtlasDocumentStorageService(settings)
    assert service.settings == settings
    assert service._client is None


def test_get_client_without_credentials(service):
    """Test getting client without credentials path"""
    with patch('atlas_shared_app.services.atlas_document_storage_service.storage.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = service._get_client()

        mock_client_class.assert_called_once_with(project="test-project")
        assert client == mock_client


def test_get_client_with_credentials(settings_with_credentials):
    """Test getting client with credentials path"""
    service = AtlasDocumentStorageService(settings_with_credentials)

    with patch('atlas_shared_app.services.atlas_document_storage_service.storage.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.from_service_account_json.return_value = mock_client

        client = service._get_client()

        mock_client_class.from_service_account_json.assert_called_once_with("/path/to/credentials.json")
        assert client == mock_client


def test_get_client_cached(service):
    """Test that client is cached after first call"""
    with patch('atlas_shared_app.services.atlas_document_storage_service.storage.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # First call
        client1 = service._get_client()
        # Second call
        client2 = service._get_client()

        # Should only be called once
        mock_client_class.assert_called_once()
        assert client1 == client2


def test_upload_file(service, mock_blob):
    """Test uploading a file"""
    file_data = BytesIO(b"test content")

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.upload_file("test-bucket", file_data, "path/to/file.pdf", "application/pdf")

        assert result == "gs://test-bucket/path/to/file.pdf"
        mock_blob.upload_from_file.assert_called_once_with(file_data, content_type="application/pdf")


def test_upload_from_string(service, mock_blob):
    """Test uploading string data"""
    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.upload_from_string("test-bucket", "test content", "path/to/file.txt", "text/plain")

        assert result == "gs://test-bucket/path/to/file.txt"
        mock_blob.upload_from_string.assert_called_once_with("test content", content_type="text/plain")


def test_download_file(service, mock_blob):
    """Test downloading a file as bytes"""
    mock_blob.download_as_bytes.return_value = b"test content"

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.download_file("test-bucket", "path/to/file.txt")

        assert result == b"test content"
        mock_blob.download_as_bytes.assert_called_once()


def test_download_to_file(service, mock_blob):
    """Test downloading a file to a file object"""
    destination = BytesIO()

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        service.download_to_file("test-bucket", "path/to/file.txt", destination)

        mock_blob.download_to_file.assert_called_once_with(destination)


def test_delete_file_exists(service, mock_blob):
    """Test deleting an existing file"""
    mock_blob.exists.return_value = True

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.delete_file("test-bucket", "path/to/file.txt")

        assert result is True
        mock_blob.delete.assert_called_once()


def test_delete_file_not_exists(service, mock_blob):
    """Test deleting a non-existent file"""
    mock_blob.exists.return_value = False

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.delete_file("test-bucket", "path/to/nonexistent.txt")

        assert result is False
        mock_blob.delete.assert_not_called()


def test_file_exists_true(service, mock_blob):
    """Test checking if file exists when it does"""
    mock_blob.exists.return_value = True

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.file_exists("test-bucket", "path/to/file.txt")

        assert result is True


def test_file_exists_false(service, mock_blob):
    """Test checking if file exists when it doesn't"""
    mock_blob.exists.return_value = False

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.file_exists("test-bucket", "path/to/nonexistent.txt")

        assert result is False


def test_get_signed_url(service, mock_blob):
    """Test generating a signed URL"""
    mock_blob.generate_signed_url.return_value = "https://signed-url.example.com"

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.get_signed_url("test-bucket", "path/to/file.txt")

        assert result == "https://signed-url.example.com"
        mock_blob.generate_signed_url.assert_called_once()


def test_get_signed_url_custom_expiration(service, mock_blob):
    """Test generating a signed URL with custom expiration"""
    mock_blob.generate_signed_url.return_value = "https://signed-url.example.com"

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.get_signed_url("test-bucket", "path/to/file.txt", expiration=7200)

        assert result == "https://signed-url.example.com"
        mock_blob.generate_signed_url.assert_called_once_with(
            expiration=timedelta(seconds=7200),
            method="GET"
        )


def test_get_upload_signed_url(service, mock_blob):
    """Test generating a signed URL for upload"""
    mock_blob.generate_signed_url.return_value = "https://upload-url.example.com"

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.get_upload_signed_url("test-bucket", "path/to/upload.pdf", "application/pdf")

        assert result == "https://upload-url.example.com"
        mock_blob.generate_signed_url.assert_called_once()


def test_list_files(service):
    """Test listing files in bucket"""
    mock_blob1 = MagicMock()
    mock_blob2 = MagicMock()

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.list_blobs.return_value = [mock_blob1, mock_blob2]
        mock_get_client.return_value = mock_client

        result = service.list_files("test-bucket", prefix="path/", delimiter="/", max_results=10)

        assert len(result) == 2
        mock_client.list_blobs.assert_called_once_with(
            "test-bucket",
            prefix="path/",
            delimiter="/",
            max_results=10
        )


def test_copy_file(service, mock_blob):
    """Test copying a file"""
    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.copy_file("test-bucket", "source/file.txt", "dest/file.txt")

        assert result == "gs://test-bucket/dest/file.txt"
        mock_bucket.copy_blob.assert_called_once()


def test_move_file(service, mock_blob):
    """Test moving a file"""
    mock_blob.exists.return_value = True

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.move_file("test-bucket", "source/file.txt", "dest/file.txt")

        assert result == "gs://test-bucket/dest/file.txt"
        mock_bucket.copy_blob.assert_called_once()
        mock_blob.delete.assert_called_once()


def test_get_metadata_exists(service, mock_blob):
    """Test getting metadata for an existing file"""
    mock_blob.exists.return_value = True

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.get_metadata("test-bucket", "path/to/file.txt")

        assert result is not None
        assert result["name"] == "test-file.pdf"
        assert result["size"] == 1024
        mock_blob.reload.assert_called_once()


def test_get_metadata_not_exists(service, mock_blob):
    """Test getting metadata for a non-existent file"""
    mock_blob.exists.return_value = False

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        result = service.get_metadata("test-bucket", "path/to/nonexistent.txt")

        assert result is None
        mock_blob.reload.assert_not_called()


def test_get_client_error(settings):
    """Test getting client when initialization fails"""
    from google.cloud.exceptions import GoogleCloudError

    service = AtlasDocumentStorageService(settings)

    with patch('atlas_shared_app.services.atlas_document_storage_service.storage.Client') as mock_client_class:
        mock_client_class.side_effect = GoogleCloudError("Failed to initialize")

        with pytest.raises(GoogleCloudError):
            service._get_client()


def test_upload_file_gcp_error(service, mock_blob):
    """Test uploading a file when GCP error occurs"""
    from google.cloud.exceptions import GoogleCloudError
    from io import BytesIO

    file_data = BytesIO(b"test content")
    mock_blob.upload_from_file.side_effect = GoogleCloudError("Upload failed")

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        with pytest.raises(GoogleCloudError):
            service.upload_file("test-bucket", file_data, "path/to/file.pdf")


def test_upload_from_string_gcp_error(service, mock_blob):
    """Test uploading string data when GCP error occurs"""
    from google.cloud.exceptions import GoogleCloudError

    mock_blob.upload_from_string.side_effect = GoogleCloudError("Upload failed")

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        with pytest.raises(GoogleCloudError):
            service.upload_from_string("test-bucket", "test content", "path/to/file.txt")


def test_download_file_not_found(service, mock_blob):
    """Test downloading a file when not found"""
    from google.cloud.exceptions import NotFound

    mock_blob.download_as_bytes.side_effect = NotFound("File not found")

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        with pytest.raises(NotFound):
            service.download_file("test-bucket", "path/to/nonexistent.txt")


def test_download_file_gcp_error(service, mock_blob):
    """Test downloading a file when GCP error occurs"""
    from google.cloud.exceptions import GoogleCloudError

    mock_blob.download_as_bytes.side_effect = GoogleCloudError("Download failed")

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        with pytest.raises(GoogleCloudError):
            service.download_file("test-bucket", "path/to/file.txt")


def test_download_to_file_not_found(service, mock_blob):
    """Test downloading to file when not found"""
    from google.cloud.exceptions import NotFound
    from io import BytesIO

    destination = BytesIO()
    mock_blob.download_to_file.side_effect = NotFound("File not found")

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        with pytest.raises(NotFound):
            service.download_to_file("test-bucket", "path/to/nonexistent.txt", destination)


def test_download_to_file_gcp_error(service, mock_blob):
    """Test downloading to file when GCP error occurs"""
    from google.cloud.exceptions import GoogleCloudError
    from io import BytesIO

    destination = BytesIO()
    mock_blob.download_to_file.side_effect = GoogleCloudError("Download failed")

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        with pytest.raises(GoogleCloudError):
            service.download_to_file("test-bucket", "path/to/file.txt", destination)


def test_delete_file_gcp_error(service, mock_blob):
    """Test deleting a file when GCP error occurs"""
    from google.cloud.exceptions import GoogleCloudError

    mock_blob.exists.return_value = True
    mock_blob.delete.side_effect = GoogleCloudError("Delete failed")

    with patch.object(service, '_get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_get_client.return_value = mock_client

        with pytest.raises(GoogleCloudError):
            service.delete_file("test-bucket", "path/to/file.txt")
