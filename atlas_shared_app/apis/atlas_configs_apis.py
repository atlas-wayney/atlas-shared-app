from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Security, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine

from ..database.atlas_asyncdb import get_engine
from ..entities.atlas_configs import AtlasConfigsReq, AtlasConfigsRes
from ..entities.atlas_user import AtlasUserRes
from ..utils.app_utils.security import verify_viewer, verify_editor
from ..services.atlas_configs_service import AtlasConfigsService

router = APIRouter(prefix="/atlas-configs/v1", tags=["atlas-configs"])


def register_configs_apis(app: FastAPI, prefix: str):
    """
    Register configs APIs with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    logger.info("Register configs APIs with the FastAPI app")
    app.include_router(router, prefix=prefix)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AtlasConfigsRes)
async def create_config(
    payload: AtlasConfigsReq,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)],
):
    """Create a new config"""
    service = AtlasConfigsService(engine)
    config = await service.create(payload, curr_user)
    return config


@router.get("/{entity_type}/{field_name}", response_model=AtlasConfigsRes)
async def get_config(
    entity_type: str,
    field_name: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get a config by entity_type and field_name"""
    service = AtlasConfigsService(engine)
    configs_dict = await service.get(entity_type, curr_user)

    if field_name not in configs_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config for entity_type={entity_type} and field_name={field_name} not found"
        )

    return configs_dict[field_name]


@router.get("/{entity_type}", response_model=list[AtlasConfigsRes])
async def get_configs_by_type(
    entity_type: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)]
):
    """Get all configs for a specific entity type"""
    service = AtlasConfigsService(engine)
    return await service.get_by_entity_type(entity_type, curr_user)


@router.get("/", response_model=list[AtlasConfigsRes])
async def list_configs(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_viewer)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List all configs"""
    service = AtlasConfigsService(engine)
    return await service.get_all(skip=skip, limit=limit, curr_user=curr_user)


@router.put("/{entity_type}/{field_name}", response_model=AtlasConfigsRes)
async def update_config(
    entity_type: str,
    field_name: str,
    payload: AtlasConfigsReq,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)]
):
    """Update a config"""
    service = AtlasConfigsService(engine)

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updated = await service.update(entity_type, field_name, update_data, curr_user)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config for entity_type={entity_type} and field_name={field_name} not found"
        )
    return updated


@router.delete("/{entity_type}/{field_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    entity_type: str,
    field_name: str,
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    curr_user: Annotated[AtlasUserRes, Depends(verify_editor)]
):
    """Delete a config"""
    service = AtlasConfigsService(engine)

    success = await service.delete(entity_type, field_name, curr_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config for entity_type={entity_type} and field_name={field_name} not found"
        )
    return None
