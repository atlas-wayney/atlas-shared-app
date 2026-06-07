from typing import List, Optional

import httpx
from fastapi import status
from loguru import logger

from ..entities.atlas_client import AtlasClientRes
from ..settings.atlas_identity_settings import AtlasIdentitySettings


class AtlasClientService:
    """Service class for fetching Client data from external API."""

    def __init__(self, settings: AtlasIdentitySettings):
        self.settings = settings
        self.base_url = settings.base_url.rstrip("/")
        self.timeout = settings.timeout

    async def get_all(self, token: Optional[str] = None) -> List[AtlasClientRes]:
        """
        Fetch all clients from the API.

        Args:
            token: Optional JWT token for authentication

        Returns:
            List of AtlasClientRes objects
        """
        headers = self._build_headers(token)
        logger.debug("Fetching all clients from API")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/clients", headers=headers)
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    logger.warning("Clients endpoint returned 404")
                    return []
                response.raise_for_status()
                data = response.json()
                logger.info("Successfully fetched {} clients", len(data))
                return [AtlasClientRes(**item) for item in data]
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching clients: status={}, url={}",
                e.response.status_code,
                e.request.url
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error fetching clients: {}", str(e))
            raise

    async def get_by_id(
        self, client_id: str, token: Optional[str] = None
    ) -> Optional[AtlasClientRes]:
        """
        Fetch a single client by ID from the API.

        Args:
            client_id: The client ID to fetch
            token: Optional JWT token for authentication

        Returns:
            AtlasClientRes if found, None otherwise
        """
        headers = self._build_headers(token)
        logger.debug("Fetching client by ID: {}", client_id)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/clients/{client_id}", headers=headers
                )
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    logger.warning("Client not found: {}", client_id)
                    return None
                response.raise_for_status()
                data = response.json()
                logger.debug("Successfully fetched client: {}", client_id)
                return AtlasClientRes(**data)
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching client {}: status={}",
                client_id,
                e.response.status_code
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error fetching client {}: {}", client_id, str(e))
            raise

    def _build_headers(self, token: Optional[str] = None) -> dict:
        """Build request headers with optional authentication."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
