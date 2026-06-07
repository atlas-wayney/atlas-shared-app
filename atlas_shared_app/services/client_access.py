from typing import TYPE_CHECKING, Optional

from fastapi import HTTPException, status
from loguru import logger

from ..entities.atlas_user import AtlasUserRes


def is_external_user(user: AtlasUserRes) -> bool:
    """Check if the user is an external user (non-internal)."""
    return not user.internal


def get_user_client_id(user: AtlasUserRes) -> Optional[str]:
    """Get the client_id for external users, None for internal users."""
    if is_external_user(user):
        return user.client_id
    return None


def validate_client_access(user: AtlasUserRes, resource_client_id: Optional[str]) -> None:
    """
    Validate that an external user has access to a resource based on client_id.

    Raises HTTPException 403 if external user tries to access another client's data.
    Internal users always have access.
    """
    if is_external_user(user):
        if resource_client_id is None:
            logger.warning(
                "External user {} attempted access to resource without client association",
                user.user_id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External users cannot access resources without a client association"
            )
        if user.client_id != resource_client_id:
            logger.warning(
                "External user {} from client {} attempted access to resource from client {}",
                user.user_id,
                user.client_id,
                resource_client_id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
    logger.debug(
        "Client access validated: user={}, user_client={}, resource_client={}",
        user.user_id,
        user.client_id,
        resource_client_id
    )


def get_client_filter_for_user(user: AtlasUserRes) -> Optional[str]:
    """
    Get client_id filter value for queries.

    Returns:
        - For external users: their client_id (to filter results)
        - For internal users: None (no filtering needed)
    """
    if is_external_user(user):
        return user.client_id
    return None
