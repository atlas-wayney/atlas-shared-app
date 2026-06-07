from typing import Callable

import jwt
from fastapi import Request, status
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..settings.atlas_identity_settings import AtlasIdentitySettings
from ..shared_services.atlas_user_service import AtlasUserService


class AuthMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for JWT authentication.

    This middleware validates JWT tokens and attaches user information to the request state.
    """

    def __init__(
        self,
        app,
        settings: AtlasIdentitySettings,
    ):
        """
        Initialize the authentication middleware.

        Args:
            app: The FastAPI application
            settings: Access matrix settings containing JWT configuration
        """
        super().__init__(app)
        self.user_service = AtlasUserService(settings)
        self.public_paths = settings.public_paths

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process the request through the middleware.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response from the next handler
        """
        # Skip authentication for public paths
        if self._is_public_path(request.url.path):
            logger.debug("Public path accessed: {}", request.url.path)
            request.state.user = None
            return await call_next(request)

        # Extract and validate token
        authorization = request.headers.get("Authorization")
        if authorization:
            try:
                user = self.user_service.get_user_from_header(authorization)
                request.state.user = user
                logger.debug(
                    "User authenticated: user_id={}, client_id={}",
                    user.user_id,
                    user.client_id
                )
            except ValueError as e:
                logger.warning(
                    "Invalid authorization header format: path={}",
                    request.url.path
                )
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": f"Invalid or expired token: {str(e)}"},
                )
            except jwt.ExpiredSignatureError:
                logger.warning("Expired JWT token: path={}", request.url.path)
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token has expired"},
                )
            except jwt.InvalidTokenError as e:
                logger.warning(
                    "Invalid JWT token: path={}, error={}",
                    request.url.path,
                    str(e)
                )
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": f"Invalid token: {str(e)}"},
                )
        else:
            logger.warning("Missing authorization header: path={}", request.url.path)
            request.state.user = None
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Access token is missing"},
            )

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """Check if the path is public and doesn't require authentication."""
        return any(path.startswith(public) for public in self.public_paths)

