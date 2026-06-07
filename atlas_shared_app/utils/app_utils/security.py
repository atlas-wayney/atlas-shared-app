from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from loguru import logger

from atlas_shared_app.entities.atlas_base_enums import AppEnum, EntityStatus, UserAccess
from atlas_shared_app.entities.atlas_user import AtlasUserRes
from atlas_shared_app.settings.atlas_settings import AtlasSettings, get_settings

security_scheme = HTTPBearer()


async def verify_user(
    request: Request,
    settings: Annotated[AtlasSettings, Depends(get_settings)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    security_scopes: SecurityScopes,
) -> AtlasUserRes:
    """
    FastAPI dependency that verifies the user from request state.

    Use this dependency in route handlers to get the authenticated user.
    The AuthMiddleware must be applied for this to work.

    Args:
        request: The FastAPI request object
        credentials: HTTP Bearer credentials (for Swagger UI integration)

    Returns:
        AtlasUserRes for the authenticated user

    Raises:
        HTTPException: 401 if user is not authenticated
    """
    user = getattr(request.state, "user", None)
    if user is None:
        logger.warning("Authentication required but no user in request state")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    curr_user: AtlasUserRes = user
    role = curr_user.roles.get(AppEnum(settings.app_id))
    if not role:
        logger.warning(
            "User {} lacks role for app {}: available_apps={}",
            curr_user.user_id,
            settings.app_id,
            list(curr_user.roles.keys())
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have roles for this application",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_scopes = curr_user.scopes.get(AppEnum(settings.app_id), [])
    for scope in security_scopes.scopes:
        if scope not in user_scopes:
            logger.warning(
                "User {} missing required scope {}: user_scopes={}, required={}",
                curr_user.user_id,
                scope,
                user_scopes,
                security_scopes.scopes
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": "Bearer"},
            )

    logger.debug(
        "User {} authorized with scopes: {}",
        curr_user.user_id,
        security_scopes.scopes
    )
    return user

async def verify_viewer(
    curr_user: Annotated[AtlasUserRes, Security(verify_user, scopes=[UserAccess.VIEW])],
) -> AtlasUserRes:
    if curr_user.user_status != EntityStatus.ACTIVE:
        logger.warning("Inactive user attempted view access: {}", curr_user.user_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return curr_user


async def verify_editor(
    curr_user: Annotated[AtlasUserRes, Security(verify_user, scopes=[UserAccess.EDIT])],
) -> AtlasUserRes:
    if curr_user.user_status != EntityStatus.ACTIVE:
        logger.warning("Inactive user attempted edit access: {}", curr_user.user_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return curr_user


async def verify_admin(
    curr_user: Annotated[AtlasUserRes, Security(verify_user, scopes=[UserAccess.ADMIN])],
) -> AtlasUserRes:
    if curr_user.user_status != EntityStatus.ACTIVE:
        logger.warning("Inactive user attempted admin access: {}", curr_user.user_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return curr_user
