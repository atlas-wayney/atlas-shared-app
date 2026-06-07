from typing import Optional, BinaryIO
from datetime import timedelta

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError, NotFound
from google.cloud.storage import Blob
from loguru import logger

from ..settings.atlas_document_settings import AtlasDocumentSettings


class AtlasDocumentStorageService:
    """Service class for GCP Cloud Storage document operations"""

    def __init__(self, settings: AtlasDocumentSettings):
        self.settings = settings
        self._client: Optional[storage.Client] = None

    def _get_client(self) -> storage.Client:
        """Get or create the GCP Storage client."""
        if self._client is None:
            logger.debug("Initializing GCP Storage client")
            try:
                if self.settings.credentials_path:
                    self._client = storage.Client.from_service_account_json(
                        self.settings.credentials_path
                    )
                else:
                    self._client = storage.Client(project=self.settings.project_id)
                logger.info("GCP Storage client initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize GCP Storage client: {}", str(e))
                raise
        return self._client

    def upload_file(
        self,
        bucket: str,
        file_data: BinaryIO,
        destination_path: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload a file to GCP Cloud Storage.

        Args:
            bucket: Bucket name
            file_data: File-like object to upload
            destination_path: Path in the bucket where the file will be stored
            content_type: MIME type of the file

        Returns:
            The gs:// path of the uploaded file
        """
        logger.debug("Uploading file to gs://{}/{}", bucket, destination_path)
        try:
            blob = self._get_client().bucket(bucket).blob(destination_path)
            blob.upload_from_file(file_data, content_type=content_type)
            logger.info("File uploaded successfully: gs://{}/{}", bucket, destination_path)
            return f"gs://{bucket}/{destination_path}"
        except GoogleCloudError as e:
            logger.error(
                "GCP error uploading file to gs://{}/{}: {}",
                bucket,
                destination_path,
                str(e)
            )
            raise

    def upload_from_string(
        self,
        bucket: str,
        data: str | bytes,
        destination_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload string or bytes data to GCP Cloud Storage.

        Args:
            bucket: Bucket name
            data: String or bytes data to upload
            destination_path: Path in the bucket where the file will be stored
            content_type: MIME type of the file

        Returns:
            The gs:// path of the uploaded file
        """
        logger.debug("Uploading data to gs://{}/{}", bucket, destination_path)
        try:
            blob = self._get_client().bucket(bucket).blob(destination_path)
            blob.upload_from_string(data, content_type=content_type)
            logger.info("Data uploaded successfully: gs://{}/{}", bucket, destination_path)
            return f"gs://{bucket}/{destination_path}"
        except GoogleCloudError as e:
            logger.error(
                "GCP error uploading data to gs://{}/{}: {}",
                bucket,
                destination_path,
                str(e)
            )
            raise

    def download_file(self, bucket: str, source_path: str) -> bytes:
        """
        Download a file from GCP Cloud Storage.

        Args:
            bucket: Bucket name
            source_path: Path in the bucket to download from

        Returns:
            The file contents as bytes
        """
        logger.debug("Downloading file from gs://{}/{}", bucket, source_path)
        try:
            blob = self._get_client().bucket(bucket).blob(source_path)
            data = blob.download_as_bytes()
            logger.debug("File downloaded successfully: gs://{}/{}", bucket, source_path)
            return data
        except NotFound:
            logger.warning("File not found: gs://{}/{}", bucket, source_path)
            raise
        except GoogleCloudError as e:
            logger.error(
                "GCP error downloading file from gs://{}/{}: {}",
                bucket,
                source_path,
                str(e)
            )
            raise

    def download_to_file(self, bucket: str, source_path: str, destination_file: BinaryIO) -> None:
        """
        Download a file from GCP Cloud Storage to a file-like object.

        Args:
            bucket: Bucket name
            source_path: Path in the bucket to download from
            destination_file: File-like object to write to
        """
        logger.debug("Downloading file to file object from gs://{}/{}", bucket, source_path)
        try:
            blob = self._get_client().bucket(bucket).blob(source_path)
            blob.download_to_file(destination_file)
            logger.debug("File downloaded to file object successfully: gs://{}/{}", bucket, source_path)
        except NotFound:
            logger.warning("File not found: gs://{}/{}", bucket, source_path)
            raise
        except GoogleCloudError as e:
            logger.error(
                "GCP error downloading file from gs://{}/{}: {}",
                bucket,
                source_path,
                str(e)
            )
            raise

    def delete_file(self, bucket: str, file_path: str) -> bool:
        """
        Delete a file from GCP Cloud Storage.

        Args:
            bucket: Bucket name
            file_path: Path in the bucket to delete

        Returns:
            True if deleted successfully, False if file not found
        """
        logger.debug("Deleting file: gs://{}/{}", bucket, file_path)
        try:
            blob = self._get_client().bucket(bucket).blob(file_path)
            if blob.exists():
                blob.delete()
                logger.info("File deleted successfully: gs://{}/{}", bucket, file_path)
                return True
            logger.warning("File not found for deletion: gs://{}/{}", bucket, file_path)
            return False
        except GoogleCloudError as e:
            logger.error(
                "GCP error deleting file gs://{}/{}: {}",
                bucket,
                file_path,
                str(e)
            )
            raise

    def file_exists(self, bucket: str, file_path: str) -> bool:
        """
        Check if a file exists in GCP Cloud Storage.

        Args:
            bucket: Bucket name
            file_path: Path in the bucket to check

        Returns:
            True if file exists, False otherwise
        """
        blob = self._get_client().bucket(bucket).blob(file_path)
        return blob.exists()

    def get_signed_url(
        self,
        bucket: str,
        file_path: str,
        expiration: Optional[int] = None,
        method: str = "GET",
    ) -> str:
        """
        Generate a signed URL for a file.

        Args:
            bucket: Bucket name
            file_path: Path in the bucket
            expiration: URL expiration time in seconds (defaults to settings value)
            method: HTTP method for the signed URL (GET, PUT, etc.)

        Returns:
            Signed URL string
        """
        blob = self._get_client().bucket(bucket).blob(file_path)
        exp_seconds = expiration or self.settings.signed_url_expiration
        return blob.generate_signed_url(
            expiration=timedelta(seconds=exp_seconds),
            method=method,
        )

    def get_upload_signed_url(
        self,
        bucket: str,
        file_path: str,
        content_type: str,
        expiration: Optional[int] = None,
    ) -> str:
        """
        Generate a signed URL for uploading a file.

        Args:
            bucket: Bucket name
            file_path: Path in the bucket where the file will be uploaded
            content_type: MIME type of the file to upload
            expiration: URL expiration time in seconds

        Returns:
            Signed URL string for PUT request
        """
        blob = self._get_client().bucket(bucket).blob(file_path)
        exp_seconds = expiration or self.settings.signed_url_expiration
        return blob.generate_signed_url(
            expiration=timedelta(seconds=exp_seconds),
            method="PUT",
            content_type=content_type,
        )

    def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> list[Blob]:
        """
        List files in the bucket.

        Args:
            bucket: Bucket name
            prefix: Filter results to objects beginning with this prefix
            delimiter: Delimiter for hierarchical listing (e.g., '/')
            max_results: Maximum number of results to return

        Returns:
            List of Blob objects
        """
        blobs = self._get_client().list_blobs(
            bucket,
            prefix=prefix,
            delimiter=delimiter,
            max_results=max_results,
        )
        return list(blobs)

    def copy_file(self, bucket: str, source_path: str, destination_path: str) -> str:
        """
        Copy a file within the bucket.

        Args:
            bucket: Bucket name
            source_path: Source path in the bucket
            destination_path: Destination path in the bucket

        Returns:
            The gs:// path of the copied file
        """
        bucket_obj = self._get_client().bucket(bucket)
        source_blob = bucket_obj.blob(source_path)
        bucket_obj.copy_blob(source_blob, bucket_obj, destination_path)
        return f"gs://{bucket}/{destination_path}"

    def move_file(self, bucket: str, source_path: str, destination_path: str) -> str:
        """
        Move a file within the bucket (copy then delete).

        Args:
            bucket: Bucket name
            source_path: Source path in the bucket
            destination_path: Destination path in the bucket

        Returns:
            The gs:// path of the moved file
        """
        self.copy_file(bucket, source_path, destination_path)
        self.delete_file(bucket, source_path)
        return f"gs://{bucket}/{destination_path}"

    def get_metadata(self, bucket: str, file_path: str) -> Optional[dict]:
        """
        Get metadata for a file.

        Args:
            bucket: Bucket name
            file_path: Path in the bucket

        Returns:
            Dictionary with file metadata, or None if file doesn't exist
        """
        blob = self._get_client().bucket(bucket).blob(file_path)
        if not blob.exists():
            return None

        blob.reload()
        return {
            "name": blob.name,
            "size": blob.size,
            "content_type": blob.content_type,
            "created": blob.time_created,
            "updated": blob.updated,
            "md5_hash": blob.md5_hash,
            "etag": blob.etag,
        }
