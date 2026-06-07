from typing import Annotated, Optional
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine

from atlas_shared_app.entities.atlas_user import AtlasUserRes
from atlas_shared_app.utils.app_utils.security import verify_viewer

from ..database.atlas_asyncdb import get_engine
from ..entities.atlas_case import AtlasCaseStatus, AtlasCaseRes
from ..services.atlas_case_service import AtlasCaseService
from ..settings.atlas_settings import get_case_settings

router = APIRouter(prefix="/atlas-cases/v1", tags=["atlas-cases"])


def register_case_apis(app: FastAPI, prefix: str):
    """
    Register case APIs with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    logger.info("Register case APIs with the FastAPI app")
    app.include_router(router, prefix=prefix)


@router.get("/{case_id}", response_model=AtlasCaseRes)
async def get_case(
    case_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get a case by ID"""
    service = AtlasCaseService(engine)
    case = await service.get_by_id(case_id, curr_user)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case {case_id} not found")
    return case


@router.get("/", response_model=list[AtlasCaseRes])
async def list_cases(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    case_status: Optional[str] = None,
    client_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    assigned_user_id: Optional[str] = None,
):
    """List all cases with optional filtering"""
    service = AtlasCaseService(engine)
    return await service.get_all(
        skip=skip,
        limit=limit,
        case_status=case_status,
        client_id=client_id,
        entity_type=entity_type,
        entity_id=entity_id,
        assigned_user_id=assigned_user_id,
        curr_user=curr_user,
    )


@router.get("/client/{client_id}", response_model=list[AtlasCaseRes])
async def get_cases_by_client(
    client_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get all cases for a specific client"""
    service = AtlasCaseService(engine)
    return await service.get_by_client_id(client_id, curr_user)


@router.get("/user/{user_id}", response_model=list[AtlasCaseRes])
async def get_cases_by_assigned_user(
    user_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get all cases assigned to a specific user"""
    service = AtlasCaseService(engine)
    return await service.get_by_assigned_user_id(user_id, curr_user)


@router.get("/status/{status}", response_model=list[AtlasCaseRes])
async def get_cases_by_status(
    status: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get all cases with a specific status"""
    service = AtlasCaseService(engine)
    try:
        case_status = AtlasCaseStatus(status)
        return await service.get_by_status(case_status, curr_user)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {status}")
