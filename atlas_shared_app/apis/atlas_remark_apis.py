from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine

from ..database.atlas_asyncdb import get_engine
from ..entities.atlas_remark import AtlasRemarkReq, AtlasRemarkRes
from ..entities.atlas_user import AtlasUserRes
from ..utils.app_utils.security import verify_viewer, verify_editor
from ..services.atlas_remark_service import AtlasRemarkService

router = APIRouter(prefix="/atlas-remarks/v1", tags=["atlas-remarks"])


def register_remark_apis(app: FastAPI, prefix: str):
    """
    Register remark APIs with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    logger.info("Register remark APIs with the FastAPI app")
    app.include_router(router, prefix=prefix)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AtlasRemarkRes)
async def create_remark(
    payload: AtlasRemarkReq,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)]
):
    """Create a new remark"""
    service = AtlasRemarkService(engine)
    remark = await service.create(payload, curr_user)
    return remark


@router.get("/{remark_id}", response_model=AtlasRemarkRes)
async def get_remark(
    remark_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get a remark by ID"""
    service = AtlasRemarkService(engine)
    remark = await service.get_by_id(remark_id, curr_user)
    if not remark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Remark {remark_id} not found")
    return remark


@router.get("/", response_model=list[AtlasRemarkRes])
async def list_remarks(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List all remarks"""
    service = AtlasRemarkService(engine)
    return await service.get_all(skip=skip, limit=limit, curr_user=curr_user)


@router.delete("/{remark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_remark(
    remark_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)]
):
    """Delete a remark"""
    service = AtlasRemarkService(engine)

    success = await service.delete(remark_id, curr_user)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Remark {remark_id} not found")
    return None


@router.get("/entity/{entity_id}", response_model=list[AtlasRemarkRes])
async def get_remarks_by_entity(
    entity_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get all remarks for a specific entity"""
    service = AtlasRemarkService(engine)
    return await service.get_by_entity_id(entity_id, curr_user)
