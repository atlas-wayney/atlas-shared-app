from typing import List, Optional

import httpx
from fastapi import status
from loguru import logger

from ..entities.atlas_subclient import AtlasSubclientRes
from ..settings.atlas_identity_settings import AtlasIdentitySettings


class AtlasSubclientService:
    """Service class for fetching Subclient data from external API."""

    def __init__(self, settings: AtlasIdentitySettings):
        self.settings = settings
        self.base_url = settings.base_url.rstrip("/")
        self.timeout = settings.timeout

    async def get_all(self, token: Optional[str] = None) -> List[AtlasSubclientRes]:
        """
        Fetch all subclients from the API.

        Args:
            token: Optional JWT token for authentication

        Returns:
            List of AtlasSubclientRes objects
        """
        headers = self._build_headers(token)
        logger.debug("Fetching all subclients from API")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/subclients", headers=headers)
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    logger.warning("Subclients endpoint returned 404")
                    return []
                response.raise_for_status()
                data = response.json()
                logger.info("Successfully fetched {} subclients", len(data))
                return [AtlasSubclientRes(**item) for item in data]
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching subclients: status={}, url={}",
                e.response.status_code,
                e.request.url
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error fetching subclients: {}", str(e))
            raise

    async def get_by_id(self, subclient_id: str, token: Optional[str] = None) -> Optional[AtlasSubclientRes]:
        """
        Fetch a single subclient by ID from the API.

        Args:
            subclient_id: The subclient ID to fetch
            token: Optional JWT token for authentication

        Returns:
            AtlasSubclientRes if found, None otherwise
        """
        headers = self._build_headers(token)
        logger.debug("Fetching subclient by ID: {}", subclient_id)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/subclients/{subclient_id}", headers=headers)
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    logger.warning("Subclient not found: {}", subclient_id)
                    return None
                response.raise_for_status()
                data = response.json()
                logger.debug("Successfully fetched subclient: {}", subclient_id)
                return AtlasSubclientRes(**data)
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching subclient {}: status={}",
                subclient_id,
                e.response.status_code
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error fetching subclient {}: {}", subclient_id, str(e))
            raise

    async def get_by_client_id(
        self, client_id: str, token: Optional[str] = None
    ) -> List[AtlasSubclientRes]:
        """
        Fetch all subclients belonging to a specific client.

        Args:
            client_id: The client ID to filter by
            token: Optional JWT token for authentication

        Returns:
            List of AtlasSubclientRes objects
        """
        headers = self._build_headers(token)
        logger.debug("Fetching subclients for client: {}", client_id)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/subclients",
                    params={"client_id": client_id},
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                logger.info("Fetched {} subclients for client {}", len(data), client_id)
                return [AtlasSubclientRes(**item) for item in data]
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching subclients for client {}: status={}",
                client_id,
                e.response.status_code
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error fetching subclients for client {}: {}", client_id, str(e))
            raise

    def _build_headers(self, token: Optional[str] = None) -> dict:
        """Build request headers with optional authentication."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
