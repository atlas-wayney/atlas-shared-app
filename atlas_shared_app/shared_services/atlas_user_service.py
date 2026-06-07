from typing import List, Optional

import httpx
import jwt
from fastapi import Request, status
from loguru import logger

from ..entities.atlas_user import AtlasUserRes
from ..entities.atlas_base_enums import AppEnum, EntityStatus, SharedEnum, UserRole
from ..settings.atlas_identity_settings import AtlasIdentitySettings


class AtlasUserService:
    """Service class for User entity and JWT token handling"""

    def __init__(self, settings: AtlasIdentitySettings):
        self.settings = settings
        self.base_url = settings.base_url.rstrip("/")
        self.timeout = settings.timeout
        self.algorithm = settings.jwt_algorithm
        self.jwt_public_key = settings.secret_jwt_public_key.get_secret_value()
        self.jwt_private_key = settings.secret_jwt_private_key.get_secret_value()

    @property
    def jwt_key(self) -> str:
        """Return the JWT public key for token verification."""
        return self.jwt_public_key

    @staticmethod
    def get_system_user() -> AtlasUserRes:
        """Return a default system user for unauthenticated requests."""
        return AtlasUserRes(
            user_id=SharedEnum.SYSTEM,
            login_id=SharedEnum.SYSTEM,
            user_name=SharedEnum.SYSTEM,
            user_status=EntityStatus.ACTIVE,
            email="",
            phone="",
            roles={
                AppEnum.ATLAS_APP_IDENTITY: UserRole.ADMIN,
                AppEnum.ATLAS_APP_NETWORK: UserRole.ADMIN,
                AppEnum.ATLAS_APP_BILLING: UserRole.ADMIN,
            },
            creater_id=SharedEnum.SYSTEM,
            creater_name=SharedEnum.SYSTEM,
            updater_id=SharedEnum.SYSTEM,
            updater_name=SharedEnum.SYSTEM
        )

    def get_user(self, token: str) -> AtlasUserRes:
        """
        Decode JWT token and return user information.

        Args:
            token: JWT token string (without 'Bearer ' prefix)

        Returns:
            AtlasUserRes: User information extracted from the token

        Raises:
            jwt.ExpiredSignatureError: If the token has expired
            jwt.InvalidTokenError: If the token is invalid
        """
        payload = jwt.decode(token, self.jwt_key, algorithms=[self.algorithm])
        user_id = payload.get("user_id")
        user_name = payload.get("user_name")

        return AtlasUserRes(
            user_id=user_id,
            login_id=payload.get("login_id", user_id),
            user_name=user_name,
            user_status=payload.get("user_status", "ACTIVE"),
            email=payload.get("email", ""),
            phone=payload.get("phone", ""),
            internal=payload.get("internal", True),
            client_id=payload.get("client_id"),
            client_name=payload.get("client_name"),
            roles=payload.get("roles", {}),
            scopes=payload.get("scopes", {}),
            creater_id=user_id,
            creater_name=user_name,
            updater_id=user_id,
            updater_name=user_name
        )

    def get_user_optional(self, token: str) -> Optional[AtlasUserRes]:
        """
        Decode JWT token and return user information, or None if invalid.

        Args:
            token: JWT token string (without 'Bearer ' prefix)

        Returns:
            AtlasUserRes or None: User information if valid, None otherwise
        """
        try:
            return self.get_user(token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def get_user_from_header(self, authorization: str) -> AtlasUserRes:
        """
        Extract and decode JWT token from Authorization header.

        Args:
            authorization: Authorization header value (e.g., 'Bearer <token>')

        Returns:
            AtlasUserRes: User information extracted from the token

        Raises:
            ValueError: If the Authorization header format is invalid
            jwt.ExpiredSignatureError: If the token has expired
            jwt.InvalidTokenError: If the token is invalid
        """
        if not authorization.startswith("Bearer "):
            raise ValueError("Invalid Authorization header format. Expected 'Bearer <token>'")

        token = authorization[7:]  # Remove 'Bearer ' prefix
        return self.get_user(token)

    def get_user_from_request(self, request: Request) -> AtlasUserRes:
        """
        Extract user from request Authorization header, or return system user.

        Args:
            request: FastAPI Request object

        Returns:
            AtlasUserRes: User from token or default system user
        """
        authorization = request.headers.get("Authorization")
        if not authorization:
            return self.get_system_user()

        try:
            return self.get_user_from_header(authorization)
        except (ValueError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return self.get_system_user()

    async def get_all(self, token: Optional[str] = None) -> List[AtlasUserRes]:
        """
        Fetch all users from the API.

        Args:
            token: Optional JWT token for authentication

        Returns:
            List of AtlasUserRes objects
        """
        headers = self._build_headers(token)
        logger.debug("Fetching all users from API")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users", headers=headers)
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    logger.warning("Users endpoint returned 404")
                    return []
                response.raise_for_status()
                data = response.json()
                logger.info("Successfully fetched {} users", len(data))
                return [AtlasUserRes(**item) for item in data]
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching users: status={}, url={}",
                e.response.status_code,
                e.request.url
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error fetching users: {}", str(e))
            raise

    async def get_by_id(self, user_id: str, token: Optional[str] = None) -> Optional[AtlasUserRes]:
        """
        Fetch a single user by ID from the API.

        Args:
            user_id: The user ID to fetch
            token: Optional JWT token for authentication

        Returns:
            AtlasUserRes if found, None otherwise
        """
        headers = self._build_headers(token)
        logger.debug("Fetching user by ID: {}", user_id)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_id}", headers=headers)
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    logger.warning("User not found: {}", user_id)
                    return None
                response.raise_for_status()
                data = response.json()
                logger.debug("Successfully fetched user: {}", user_id)
                return AtlasUserRes(**data)
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching user {}: status={}",
                user_id,
                e.response.status_code
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error fetching user {}: {}", user_id, str(e))
            raise

    async def get_by_client_id(self, client_id: str, token: Optional[str] = None) -> List[AtlasUserRes]:
        """
        Fetch all users belonging to a specific client.

        Args:
            client_id: The client ID to filter by
            token: Optional JWT token for authentication

        Returns:
            List of AtlasUserRes objects
        """
        headers = self._build_headers(token)
        logger.debug("Fetching users for client: {}", client_id)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/users",
                    params={"client_id": client_id},
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                logger.info("Fetched {} users for client {}", len(data), client_id)
                return [AtlasUserRes(**item) for item in data]
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching users for client {}: status={}",
                client_id,
                e.response.status_code
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error fetching users for client {}: {}", client_id, str(e))
            raise

    def _build_headers(self, token: Optional[str] = None) -> dict:
        """Build request headers with optional authentication."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
