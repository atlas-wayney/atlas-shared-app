from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine

from ..database.atlas_asyncdb import get_engine
from ..entities.atlas_history import AtlasHistoryReq, AtlasHistoryRes
from ..entities.atlas_user import AtlasUserRes
from ..utils.app_utils.security import verify_viewer, verify_editor
from ..services.atlas_history_service import AtlasHistoryService

router = APIRouter(prefix="/atlas-histories/v1", tags=["atlas-histories"])


def register_history_apis(app: FastAPI, prefix: str):
    """
    Register history APIs with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    logger.info("Register history APIs with the FastAPI app")
    app.include_router(router, prefix=prefix)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AtlasHistoryRes)
async def create_history(
    payload: AtlasHistoryReq,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)]
):
    """Create a new history entry"""
    service = AtlasHistoryService(engine)
    history = await service.create(payload, curr_user)
    return history


@router.get("/{history_id}", response_model=AtlasHistoryRes)
async def get_history(
    history_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get a history entry by ID"""
    service = AtlasHistoryService(engine)
    history = await service.get_by_id(history_id, curr_user)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"History {history_id} not found")
    return history


@router.get("/", response_model=list[AtlasHistoryRes])
async def list_histories(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List all history entries"""
    service = AtlasHistoryService(engine)
    return await service.get_all(skip=skip, limit=limit, curr_user=curr_user)


@router.get("/entity/{entity_id}", response_model=list[AtlasHistoryRes])
async def get_histories_by_entity(
    entity_id: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get all history entries for a specific entity"""
    service = AtlasHistoryService(engine)
    return await service.get_by_entity_id(entity_id, curr_user)
